import control as c
import time
def main():
  cmd = c.Commands()
  cmd.setup()
  for i in range(100):
    cmd.move(-200, 0)
    time.sleep(0.5)
  cmd.reset()
if __name__ == "__main__":
  main()
