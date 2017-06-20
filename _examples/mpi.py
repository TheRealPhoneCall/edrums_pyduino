def initiate_msgs(comm, size):
    midi_msgs = []
    for rank in range(size):
        midi_msgs[rank] = ""
    return midi_msgs

def mpi_transmit(comm, rank, size, data, src=0):
    try:
        for dest in range(size):
            if not dest == src:
                comm.send(data, dest)
    except Exception as e:
        print "error in transmitting message."
        print e.msg
