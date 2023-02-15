#Copyright © 2018 Naturalpoint
#
#Licensed under the Apache License, Version 2.0 (the "License")
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.


# OptiTrack NatNet direct depacketization sample for Python 3.x
#
# Uses the Python NatNetClient.py library to establish a connection (by creating a NatNetClient),
# and receive data via a NatNet connection and decode it using the NatNetClient library.

import sys
import time
from NatNetClient import NatNetClient
import DataDescriptions
import MoCapData

import numpy as np
import os


# This is a callback function that gets connected to the NatNet client
# and called once per mocap frame.
def receive_new_frame(data_dict):
    order_list=[ "frameNumber", "markerSetCount", "unlabeledMarkersCount", "rigidBodyCount", "skeletonCount",
                "labeledMarkerCount", "timecode", "timecodeSub", "timestamp", "isRecording", "trackedModelsChanged" ]
    dump_args = False
    if dump_args == True:
        out_string = "    "
        for key in data_dict:
            out_string += key + "="
            if key in data_dict :
                out_string += data_dict[key] + " "
            out_string+="/"
        print(out_string)

# This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
def receive_rigid_body_frame( new_id, position, rotation ):
    pass
    #print( "Received frame for rigid body", new_id )
    #print( "Received frame for rigid body", new_id," ",position," ",rotation )

def add_lists(totals, totals_tmp):
    totals[0]+=totals_tmp[0]
    totals[1]+=totals_tmp[1]
    totals[2]+=totals_tmp[2]
    return totals

def print_configuration(natnet_client):
    print("Connection Configuration:")
    print("  Client:          %s"% natnet_client.local_ip_address)
    print("  Server:          %s"% natnet_client.server_ip_address)
    print("  Command Port:    %d"% natnet_client.command_port)
    print("  Data Port:       %d"% natnet_client.data_port)

    if natnet_client.use_multicast:
        print("  Using Multicast")
        print("  Multicast Group: %s"% natnet_client.multicast_address)
    else:
        print("  Using Unicast")

    #NatNet Server Info
    application_name = natnet_client.get_application_name()
    nat_net_requested_version = natnet_client.get_nat_net_requested_version()
    nat_net_version_server = natnet_client.get_nat_net_version_server()
    server_version = natnet_client.get_server_version()

    print("  NatNet Server Info")
    print("    Application Name %s" %(application_name))
    print("    NatNetVersion  %d %d %d %d"% (nat_net_version_server[0], nat_net_version_server[1], nat_net_version_server[2], nat_net_version_server[3]))
    print("    ServerVersion  %d %d %d %d"% (server_version[0], server_version[1], server_version[2], server_version[3]))
    print("  NatNet Bitstream Requested")
    print("    NatNetVersion  %d %d %d %d"% (nat_net_requested_version[0], nat_net_requested_version[1],\
       nat_net_requested_version[2], nat_net_requested_version[3]))
    #print("command_socket = %s"%(str(natnet_client.command_socket)))
    #print("data_socket    = %s"%(str(natnet_client.data_socket)))


def print_commands(can_change_bitstream):
    outstring = "Commands:\n"
    outstring += "Return Data from Motive\n"
    outstring += "  x  sample X data\n"
    outstring += "  y  sample Y data\n"
    outstring += "  s  save\n"

    outstring += "q  quit\n"

    outstring += "\n"
    outstring += "EXAMPLE: PacketClient [serverIP [ clientIP [ Multicast/Unicast]]]\n"
    outstring += "         PacketClient \"192.168.10.14\" \"192.168.10.14\" Multicast\n"
    outstring += "         PacketClient \"127.0.0.1\" \"127.0.0.1\" u\n"
    outstring += "\n"
    print(outstring)

def request_data_descriptions(s_client):
    # Request the model definitions
    s_client.send_request(s_client.command_socket, s_client.NAT_REQUEST_MODELDEF,    "",  (s_client.server_ip_address, s_client.command_port) )

def test_classes():
    totals = [0,0,0]
    print("Test Data Description Classes")
    totals_tmp = DataDescriptions.test_all()
    totals=add_lists(totals, totals_tmp)
    print("")
    print("Test MoCap Frame Classes")
    totals_tmp = MoCapData.test_all()
    totals=add_lists(totals, totals_tmp)
    print("")
    print("All Tests totals")
    print("--------------------")
    print("[PASS] Count = %3.1d"%totals[0])
    print("[FAIL] Count = %3.1d"%totals[1])
    print("[SKIP] Count = %3.1d"%totals[2])

def my_parse_args(arg_list, args_dict):
    # set up base values
    arg_list_len=len(arg_list)
    if arg_list_len>1:
        args_dict["serverAddress"] = arg_list[1]
        if arg_list_len>2:
            args_dict["clientAddress"] = arg_list[2]
        if arg_list_len>3:
            if len(arg_list[3]):
                args_dict["use_multicast"] = True
                if arg_list[3][0].upper() == "U":
                    args_dict["use_multicast"] = False

    return args_dict



if __name__ == "__main__":
    print(f" ============ init script ============= ")

    # iteraction data to be stored
    X_init_pos_list = [] #K_push x NUM_NODES x 3
    Y_final_pos_list = [] #K_push x NUM_NODES x 3

    SAVE_PATH = r"C:\Users\Mark\Desktop\NatNetSDK\Samples\PythonClient\dataset\\"

    try:

        optionsDict = {}
        optionsDict["clientAddress"] = "127.0.0.1"
        optionsDict["serverAddress"] = "127.0.0.1"
        optionsDict["use_multicast"] = True

        # This will create a new NatNet client
        optionsDict = my_parse_args(sys.argv, optionsDict)

        streaming_client = NatNetClient()
        streaming_client.set_client_address(optionsDict["clientAddress"])
        streaming_client.set_server_address(optionsDict["serverAddress"])
        streaming_client.set_use_multicast(optionsDict["use_multicast"])

        # Configure the streaming client to call our rigid body handler on the emulator to send data out.
        streaming_client.new_frame_listener = receive_new_frame
        streaming_client.rigid_body_listener = receive_rigid_body_frame

        # Start up the streaming client now that the callbacks are set up.
        # This will run perpetually, and operate on a separate thread.
        is_running = streaming_client.run()
        if not is_running:
            print("ERROR: Could not start streaming client.")
            try:
                sys.exit(1)
            except SystemExit:
                print("...")
            finally:
                print("exiting")

        is_looping = True
        time.sleep(1)
        if streaming_client.connected() is False:
            print("ERROR: Could not connect properly.  Check that Motive streaming is on.")
            try:
                sys.exit(2)
            except SystemExit:
                print("...")
            finally:
                print("exiting")

        print_configuration(streaming_client)
        print("\n")
        print_commands(streaming_client.can_change_bitstream_version())

        #by default, set print level ALWAYS
        streaming_client.set_print_level(1)

        NUM_MARKERS = 6

        while is_looping:
            inchars = input('Enter command or (\'h\' for list of commands)\n')
            if len(inchars)>0:
                c1 = inchars[0].lower()
                if c1 == 'x':
                    print(f" ******* start X sample ******* ")
                    streaming_client.sample_data = True
                    time.sleep(0.1) #to prevent grabbing empty data
                    X = streaming_client.get_labeled_marker_data()

                    if len(X) == NUM_MARKERS:
                        X_init_pos_list.append(X)
                        # print(f" X_init_pos_list {X_init_pos_list}")
                        print(f"size of X_init_pos_list: {len(X_init_pos_list)} x {len(X_init_pos_list[0])} x  {len(X_init_pos_list[0][0])} ") #
                    else:
                        print(f"discarding data b/c num markers detected does not match")


                elif c1 == 'y':
                    print(f" ******* start Y sample ******* ")
                    streaming_client.sample_data = True
                    time.sleep(0.1) #to prevent grabbing empty data
                    Y = streaming_client.get_labeled_marker_data()
                    if len(Y) == NUM_MARKERS:
                        Y_final_pos_list.append(Y)
                        # print(f" X_init_pos_list {X_init_pos_list}")
                        print(f"size of Y_final_pos_list: {len(Y_final_pos_list)} x {len(Y_final_pos_list[0])} x  {len(Y_final_pos_list[0][0])} ") #
                    else:
                        print(f"discarding data b/c num markers detected does not match")

                elif c1 == 's':
                    print(f" ******* saved data ******* ")
                    X_init_pos_list_np = np.asarray(X_init_pos_list)
                    Y_final_pos_list_np = np.asarray(Y_final_pos_list)
                    print(f"Y_final_pos_list_np {Y_final_pos_list_np.shape}") #K PUSH x NUM NODE x 3 pos

                    np.save(SAVE_PATH + 'final_X', X_init_pos_list_np)
                    np.save(SAVE_PATH + 'final_Y', Y_final_pos_list_np)
                    #quit
                    is_looping = False
                    streaming_client.shutdown()
                    break

                elif c1 == 'q':
                    is_looping = False
                    streaming_client.shutdown()
                    break
                else:
                    print("Error: Command %s not recognized"%c1)
                print("Ready...\n")
        print("exiting")
    
    except KeyboardInterrupt:
        print(f" =========== Interrupted =========== ")
        is_looping = False
        streaming_client.shutdown()
        sys.exit(0) 
