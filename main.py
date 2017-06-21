import argparse
import shutil
import mido

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-ld', '--list-devices', action='store_true',
                        help='list audio devices and exit')
    parser.add_argument('-d', '--device', type=int_or_str,
                        help='input device (numeric ID or substring)')
    parser.add_argument('-t', '--type', type=str, default='arduino_std',
                        help='what drum pad module to run (default %(default).py)')
    parser.add_argument('-pc', '--pad-config', type=str, default='basic.json',
                        help='the pad configuration json file (default %(default))')
    parser.add_argument('-cp', '--com-port', type=str, default='COM5',
                        help='the serial port to communicate with arduino (default %(default))')
    parser.add_argument('-br', '--baud-rate', type=int, default=115200,
                        help='the baud rate to communicate with arduino (default %(default))')    
    parser.add_argument('-lmp', '--list-midi-ports', action='store_true',
                        help='list midi output ports and exit')
    parser.add_argument('-mp', '--midi-port', type=str, default='berdrums 1',
                        help='the virtual midi port to send output msg (default %(default))')
    args = parser.parse_args()

    # try:
    import sounddevice as sd

    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)

    if args.list_midi_ports:
        mido.get_output_names()
        parser.exit(0)

    # run drum pad modules
    if args.type == 'arduino_std':
        import arduino_std.main as arduino_std
        arduino_std.main(args.com_port, args.midi_port, args.baud_rate, args.pad_config)

    if args.type == 'arduino_firmata':
        import arduino_firmata.main as arduino_firmata
        arduino_firmata.main(args.com_port, args.midi_port, args.pad_config)

    if args.type == 'layered_triggers':
        import layered_triggers.main as layered_triggers 
        layered_triggers.main(args.com_port, args.midi_port, args.pad_config)

    # except KeyboardInterrupt:
    #     parser.exit('Interrupted by user')
    # except Exception as e:
    #     parser.exit(type(e).__name__ + ': ' + str(e))

if __name__ == '__main__':
    main()