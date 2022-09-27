# Unlock Huawei bootloader with bruteforce

## Summary

After closing the official EMUI website, which allowed you to retrieve the code to unlock the bootloader of Huawei/Honor phones, here is a python script to retrieve it by yourself.

It uses a bruteforce method, based on the Luhn algorithm and the IMEI identifier used by the manufacturer to generate the unlocking code.

The original version was developed by [SkyEmi](https://github.com/SkyEmie). I made some tweaks for saving failed attempts to file, because brutforcing is taking a **looooooong** time.

## Instructions

### Prerequisites
- Python > 3.7
- PyPI
- ADB
- Fastboot

### Connecting a device in ADB mode

1. Enable developer options in Android at your phone.

    * Go to Settings > System > About device > tap _Build number_ seven times to enable developer options.

2. Enable USB debugging and OEM unlock in Android.

    * Go to Settings > System > Developer options.

3. Connect your device to the computer 

4. Replace IMEI_OF_YOUR_DEVICE by the first IMEI of your phone in this script:
``` bash
git clone https://github.com/titulebolide/huaweiBootloaderHack.git
cd huaweiBootloaderHack
python3 unlock.py IMEI_OF_YOUR_DEVICE
```

5. Some devices have a bruteforce protection, preventing trying more than five codes. In this case, you will have to invoke the script with the option attempt-limit:
```bash
python3 unlock.py --attempt-limit 5 IMEI_OF_YOUR_DEVICE
```

6. If you want to pause the process you can simply exit the script by pressing `CTRL+C`. Write down the last shown "Attempt no.".
   - To resume invoke the script like so: `python3 --resume-count ATTEMPT_NO IMEI_OF_YOUR_DEVICE`
   - If you were using an attempt-limit use: `python3 --resume-count ATTEMPT_NO --attempt-limit 5 IMEI_OF_YOUR_DEVICE`

7. Make a few cups of coffee or tea => sleep => repeat :D

## FAQ & Troubleshooting
If adb and fastboot are not found, you can try manually setting their path with the flags `--adb` and `--fastboot`. All in all, the `python3 unlock.py --help` manual can always be resourceful.
