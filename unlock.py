import math
import subprocess
import click
import time
import sys

def luhn_checksum(imei):
  def digits_of(n):
    return [int(d) for d in str(n)]
  digits      = [int(d) for d in str(imei)]
  oddDigits   = digits[-1::-2]
  evenDigits  = digits[-2::-2]
  checksum    = 0
  checksum    += sum(oddDigits)
  for i in evenDigits:
    checksum += sum(digits_of(i * 2))
  return checksum % 10


def tryUnlockBootloader(imei, fastboot, limit_attempt = -1, resume_count_at = 0):
  unlocked = False
  countAttempts = resume_count_at
  limit_attempt = limit_attempt if limit_attempt > 0 else 40000
    
  while(unlocked == False):
    algoOEMcode = 1000000000000000 + countAttempts * int(math.sqrt(imei) * 1024)

    if countAttempts%10 == 0: 
      print(f"Attempt no. {countAttempts} with code {algoOEMcode}")

    start_time = time.time()
    answer = subprocess.run(
      [fastboot, 'oem', 'unlock', str(algoOEMcode)],
      stdout = subprocess.DEVNULL,
      stderr = subprocess.DEVNULL
    ) 
    exec_time = time.time()-start_time
    if (exec_time > 1):
      print("One attempt is taking longer than expected. Please try lowering limit-attempt or rebooting the device")

    if answer.returncode == 0:
      unlocked = True
      return algoOEMcode
    
    # reboot in bootloader mode after limit of attempts is reached
    if (countAttempts+1) % limit_attempt == 0:
      subprocess.run(
        [fastboot, 'reboot', 'bootloader'],
        stdout = subprocess.DEVNULL,
        stderr = subprocess.DEVNULL
      )
    countAttempts += 1


def get_confirm(*args, default_yes=False):
  """
  Prompt the message contained in [args] to the user
  and return the user response
  """
  yeses = ('y', 'yes', '1')
  nos = ('n', 'no', '0')
  if default_yes:
    options = "[Y/n]"
  else:
    options = "[y/N]"
  print(*args, options, end = " ")
  rep = input().lower()
  if default_yes:
    return not rep in nos
  else:
    return rep in yeses


@click.command()
@click.option('--resume-count', '-r', default=0, help="Set the attempt number at which the bruteforce should resume in case of a stop. This number is logged by the previous run. Not necessary if running for the first time.")
@click.option('--limit-attempt', '-l', default=-1, help="Set the max number of attempt to perform before rebooting. On some devices a number of 5 is necessary to prevent hitting bruteforce protection. Don't use this option to set no limit.")
@click.option('--fastboot', '-f', default='', help="Path to fastboot executable. Defaults to the one in PATH in UNIX-like, fastboot.exe on Windows")
@click.option('--adb', '-a', default='', help="Path to fastboot executable. Defaults to the one in PATH in UNIX-like, adb.exe on Windows")
@click.argument("imei")
def main(resume_count, limit_attempt, fastboot, adb, imei):
  imei = int(imei)
  if (luhn_checksum(imei) != 0):
    print("Invalid IMEI. Aborting.")
    return

  if fastboot == "":
    if sys.platform in ('linux', 'darwin'):
      fastboot = "fastboot"
    elif sys.platform in ('win32', 'cygwin'):
      fastboot = "fastboot.exe"
    else:
      print("Unsupported platform, please try setting manually fastboot and adb path")
      return
  if adb == "":
    if sys.platform in ('linux', 'darwin'):
      adb = "adb"
    elif sys.platform in ('win32', 'cygwin'):
      adb = "adb.exe"
    else:
      print("Unsupported platform, please try setting manually fastboot and adb path")

  subprocess.run([adb, 'devices'])
  
  print("Please check the following points:")
  print("   - USB DEBUG is enabled")
  print("   - OEM UNLOCK is enabled")
  print("   - Your device is backed up")
  if (not get_confirm("Confirm running ?", default_yes=True)): return

  subprocess.run(
    [adb, 'reboot', 'bootloader']
  , stdout = subprocess.DEVNULL
  , stderr = subprocess.DEVNULL
  )

  input('Press any key when your device is in fastboot mode\n')

  codeOEM = tryUnlockBootloader(imei, fastboot, limit_attempt, resume_count)

  subprocess.run([fastboot, 'getvar', 'unlocked'])
  # could also be a different command to check unlock status
  subprocess.run([fastboot, 'reboot'])

  print('\n\nDevice unlocked! OEM CODE: {0}'.format(codeOEM))
  with open("oem_code.txt", "w") as f:
    f.write(str(codeOEM))

if __name__ == '__main__':
  main()
