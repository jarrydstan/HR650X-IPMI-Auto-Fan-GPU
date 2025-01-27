import subprocess
import re
import yaml
import time
import datetime
import pynvml

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_temperature(ipmi):
    cmd = f"ipmitool -I lanplus -H {ipmi['host']} -U {ipmi['username']} -P '{ipmi['password']}' sensor | grep CPU | grep Temp"
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    gpu_temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
    print(gpu_temp)

    if process.returncode != 0:
        print(f"Error executing command: {cmd}. Error: {error}")
        return None

    output = output.decode('utf-8')
    lines = output.split('\n')
    print(lines)
    temperatures = []
    temperatures.append(float(gpu_temp))

    for line in lines:
        try:
            print(line.split('|')[1])
            if line.split('|')[1].strip() == 'na':
                temperatures.append(float(0))  
                print('The system is off, tempature is na')
                continue
        except IndexError as err:
            print(f"Error: {err}")
            continue
        if 'Temp' in line:
            temp = re.findall(r'\d+\.\d+', line)
            if temp:
                temperatures.append(float(temp[0]))

    if not temperatures:
        print("No temperature data found.")
        return None
    return max(temperatures)
def main():
    with open('HR650X.yaml', 'r') as file:
        config = yaml.safe_load(file)

    temp = get_temperature(config['ipmi'])

    if temp is None:
        print("No temperature data found.")
        return
main()

