for i in range(100):
    print(f"""<server type="{hex(i)[2:].zfill(2)}" limit="10" bootupTime="60" hourlyRate="0.4" coreCount="4" memory="16000" disk="64000" />""")
