for i in range(100):
    print('<server type="{}" limit="10"'
          'bootupTime="60" hourlyRate="0.4" coreCount="4" memory="16000" disk="64000" />'.format(hex(i)[2:].zfill(2)))
