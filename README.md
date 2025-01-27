# HR650X-IPMI-Auto-Fan

Use Python to automatically set fan speed for Lenovo HR650X Server based on CPU temps and GPU temps (Currently only set to work for 1 GPU, can be changed to use all GPUs)


This should also works for HR630X and some other Lenovo servers with the same ipmi raw code.

# Requirements

1. install ipmitool on your system
2. install pyyaml and pynvml: `pip install pyyaml nvidia-ml-py`

# Usage

```bath
python ipmi_manager.py
```


Tested on Python 3.8


# TODO

1. wrap these codes into a docker container
2. support multiple devices
