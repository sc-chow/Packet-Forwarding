import ipaddress
import copy
import os
import sys
from operator import itemgetter


# forward table then ipaddress

def main(argv, first):
    if (first == True):
        # print(sys.argv[1])
        # print(sys.argv[2])
        filename = sys.argv[1]
        destaddr = sys.argv[2]
    # ask user for destionation Ip address to be forwarded
    else:
        while True:
            try:
                destaddr = ipaddress.ip_address(
                    input("Enter in destination IP address of the packet to be forwarded:  "))
                break
            except ValueError:
                continue
        # print("Destination address",destaddr)
        while True:
            try:
                filename = input("Input name of the file (Ex:forwardTableTest1.txt): ")
                if os.path.exists(filename):
                    break
            except:
                print("That file does not exist!")
                continue

    # read routing table text
    file = open(filename, 'r')
    temp_list = []
    temp_list = [line.strip().split("\t") for line in file]
    temp_list = [[string for string in sublist if string] for sublist in temp_list]
    # print("Routing  table:",temp_list)

    # sort table according to largest to smallest mask
    rout_table = sorted(temp_list, key=itemgetter(2), reverse=True)
    print("Routing  table after sorting table from largest to smallest mask:", rout_table)

    # save original copy of the routing table
    route_table = copy.deepcopy(rout_table)

    # convert ip addresses and masks to binary in routing table
    ipaddr = [item[0] for item in rout_table]
    maskaddr = [item[2] for item in rout_table]
    # print("IP addresses from the routing table",ipaddr)
    # print("Mask from the routing table",maskaddr)
    i = 0
    while i < len(ipaddr):
        ip2bin = ".".join(map(str, ["{0:08b}".format(int(x)) for x in ipaddr[i].split(".")]))
        mask2bin = ".".join(map(str, ["{0:08b}".format(int(x)) for x in maskaddr[i].split(".")]))
        # print("IP address to binary: ",ip2bin)
        # print("Mask to binary: ",mask2bin)
        ipaddr[i] = ip2bin
        maskaddr[i] = mask2bin
        i += 1
    # print("IP addresses in binary from the routing table",ipaddr)
    # print("Mask in binary from the routing table",maskaddr)

    # convert destination IP address to binary
    destaddr = str(destaddr)
    destip2bin = ".".join(map(str, ["{0:08b}".format(int(x)) for x in destaddr.split(".")]))
    # print("Destination IP address to binary",destip2bin)

    # make a copy of the routing table for addresses in binary
    route_table_bin = rout_table

    # replace ip address in routing table to binary in route_table_bin
    for newVal, subList in zip(ipaddr, route_table_bin):
        subList[0] = newVal
    # print(route_table_bin)

    # replace mask in routing table to binary in route_table_bin
    for newVal, subList in zip(maskaddr, route_table_bin):
        subList[2] = newVal
    # print(route_table_bin)

    # bitwise AND destination address and masks
    i = 0
    matching = []
    while i < len(maskaddr):
        curr_mask = maskaddr[i]
        curr_mask_split = curr_mask.split(".")
        # print(len(curr_mask_split))
        # curr_mask_split 0-3
        dest_addr_split = destip2bin.split(".")
        # print(len(dest_addr_split))
        # dest_addr_split 0-3
        ip_addr_split = ipaddr[i].split(".")
        # print(len(ip_addr_split))
        # ip_addr_split 0-3
        and_0 = int(curr_mask_split[0], 2) & int(dest_addr_split[0], 2)
        and_0 = format(and_0, '08b')
        and_1 = int(curr_mask_split[1], 2) & int(dest_addr_split[1], 2)
        and_1 = format(and_1, '08b')
        and_2 = int(curr_mask_split[2], 2) & int(dest_addr_split[2], 2)
        and_2 = format(and_2, '08b')
        and_3 = int(curr_mask_split[3], 2) & int(dest_addr_split[3], 2)
        and_3 = format(and_3, '08b')
        if (and_0 == ip_addr_split[0] and and_1 == ip_addr_split[1] and and_2 == ip_addr_split[2] and and_3 ==
                ip_addr_split[3]):
            matching.append(ipaddr[i])
        i += 1
    # print("IP addresses that match:",matching)

    if (len(matching) > 1):
        match_0_index = ipaddr.index(matching[0])
        match_1_index = ipaddr.index(matching[1])
        match_col_0 = route_table_bin[int(match_0_index)]
        match_col_1 = route_table_bin[int(match_1_index)]
        # print(match_col_0)
        # print(match_col_1)
        pick = None
        # compare masks
        mask_0 = maskaddr[match_0_index]
        mask_1 = maskaddr[match_1_index]
        if (mask_0 == mask_1):
            pick = None
            # if its not equal then the bigger mask is the first element
            # since the table is optimized
        else:
            pick = match_col_0
            pick_index = match_0_index
        # compare metrics
        metric_0 = int(rout_table[match_0_index][3])
        metric_1 = int(rout_table[match_1_index][3])
        if (metric_0 == metric_1 and pick == None):
            pick = match_col_0
            pick_index = match_0_index
        elif (metric_1 > metric_0 and pick == None):
            pick = match_col_1
            pick_index = match_1_index
        else:
            pick = match_col_0
            pick_index = match_0_index
        # print("Routing  table after sorting table from largest to smallest mask:",rout_table)
        print("The destination IP address is ", destaddr)
        if (pick[1] == '*'):
            print("The next hop IP address is ", route_table[int(pick_index)][0])
            port = rout_table[int(pick_index)][4]
            port = int(port[-1])
            print("The port the packet will leave through is ", port)
        else:
            print("The next hop IP address is ", route_table[int(pick_index)][1])
            port = rout_table[int(pick_index)][4]
            port = int(port[-1])
            print("The port the packet will leave through is", port)

    else:
        match_index = ipaddr.index(matching[0])
        match_column = route_table_bin[int(match_index)]
        # print(match_column)
        print("The destination IP address is ", destaddr)
        if (match_column[1] == '*'):
            print("The next hop IP address is ", route_table[int(match_index)][0])
            port = rout_table[int(match_index)][4]
            port = int(port[-1])
            print("The port the packet will leave through is", port)
        else:
            print("The next hop IP address is ", route_table[int(match_index)][1])
            port = rout_table[int(match_index)][4]
            port = int(port[-1])
            print("The port the packet will leave through is", port)

    # ask user if they would like to send another packet
    if (again() == True):
        sys.argv = None
        first = False
        main(sys.argv, first)
    else:
        print("Program is terminating")
        exit()


def again():
    while True:
        answer = input("Would you like to forward another packet?(Y/N)").lower()
        try:
            if (answer == 'y'):
                return True
            elif (answer == 'n'):
                return False
            else:
                raise Exception("Invalid input! Answer Must Be 'Y' or 'N'")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    first = True
    main(sys.argv, first)
