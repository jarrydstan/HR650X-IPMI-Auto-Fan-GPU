import subprocess
import re
import yaml
import time
import datetime
import pynvml
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='ipmi_manager.log', encoding='utf-8', level=logging.INFO)

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_temperature(ipmi):
    cmd = f"ipmitool -I lanplus -H {ipmi['host']} -U {ipmi['username']} -P '{ipmi['password']}' sensor | grep CPU | grep Temp"
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    gpu_temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)

    if process.returncode != 0:
        logger.error(f"Error executing command: {cmd}. Error: {error}")
        return None

    output = output.decode('utf-8')
    lines = output.split('\n')
    temperatures = []
    temperatures.append(float(gpu_temp))

    for line in lines:
        try:
            if line.split('|')[1].strip() == 'na':
                temperatures.append(float(0))  
                logger.info('The system is off, tempature is na')
                continue
        except IndexError as err:
            logger.error(f"Error: {err}")
            continue
        if 'Temp' in line:
            temp = re.findall(r'\d+\.\d+', line)
            if temp:
                temperatures.append(float(temp[0]))

    if not temperatures:
        logger.info("No temperature data found.")
        return None
    
    # print(lines)
    # print(temperatures)
    
    return max(temperatures)


def set_fan_speed(speed, ipmi):
    cmd = f"ipmitool -I lanplus -H {ipmi['host']} -U {ipmi['username']} -P '{ipmi['password']}' raw 0x2e 0x30 00 00 {speed}"
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    if process.returncode != 0:
        logger.error(f"Error executing command: {cmd}. Error: {error}")
        return False

    return True


def get_fan_speed(temp, fan_speeds):
    for fan_speed in fan_speeds:
        if fan_speed['temp_range'][0] <= temp < fan_speed['temp_range'][1]:
            return fan_speed['speed']
    return 100


def main():
    with open('HR650X.yaml', 'r') as file:
        config = yaml.safe_load(file)

    temp = get_temperature(config['ipmi'])

    if temp is None:
        logger.warning("No temperature data found.")
        return

    speed = get_fan_speed(temp, config['fan_speeds'])

    if set_fan_speed(speed, config['ipmi']):
        logger.info(f"Set fan speed to {speed}% for CPU temperature {temp}°C")


if __name__ == "__main__":
    while True:
        print(get_timestamp(), end=' ')
        main()
        time.sleep(10)
