import sys
import os
import re
from Module.DB import *

def read_technology_file(tech: Tech, filename: str) -> None:
    """
    @brief: Parse technology information from file
    @param: tech -> technology object
    @param: filename -> technology file name
    """
    # Check if technology file exists
    if not os.path.isfile(filename):
        print("Error: technology file \'"+filename+"\' does not exists. Could not read in technology information.")
        sys.exit()

    # Read from file line by line
    match: str = None             # match flag
    file = open(filename, 'r')    # open file

    for line in file:
        # skip comment line and empty line
        if re.match(r'\s*#',line) or re.match(r'\s*\n',line):
            continue

        # start extracting content
        if match:
            # end of extract
            if re.match('end',line):
                match = None

            # extracting layers
            elif match == "layers":
                info: list = line.split()
                tech.layer[info[0]] = Layer(info[0],info[1],info[2])

            # extracting units
            elif match == "units":
                info: list = line.split()
                tech.unit[info[0]] = float(info[1])

            # extracting rules
            elif match == "rules":
                info: list = line.split()

                if rules == "minimum_width":
                    tech.min_width_rule[info[0]] = float(info[1])

                elif rules == "minimum_size":
                    tech.min_size_rule[info[0]] = float(info[1])

                elif rules == "minimum_area":
                    tech.min_area_rule[info[0]] = float(info[1])

                elif rules == "minimum_spacing":
                    if len(info) == 4:
                        tech.min_spacing_rule[(info[0],info[1],info[2])] = float(info[3])
                    else:
                        tech.min_spacing_rule[(info[0],info[1])] = float(info[2])
                
                elif rules == "minimum_enclosure":
                    if len(info) == 4:
                        tech.min_enclosure_rule[(info[0],info[1],info[2])] = float(info[3])
                    else:
                        tech.min_enclosure_rule[(info[0],info[1])] = float(info[2])
                
                elif rules == "minimum_extension":
                    tech.min_extension_rule[(info[0],info[1])] = float(info[2])

            # extracting models
            elif match == "models":   
                # seperate attributes by space
                attr: list = line.split()

                # extracting subckt information
                if attr[0] == "subckt":
                    tech.model["subckt"] = {}
                    tech.model["subckt"]["init"] = attr[1]

                # extracting device information
                else:
                    tech.model[attr[2]] = {}
                    tech.model[attr[2]]["init"] = attr[1]
                    tech.model[attr[2]]["type"] = attr[0]
                    tech.model[attr[2]]["ports"] = re.search(r'\((.+)\)',line).group(1).split()
                    
                    # get number of ports and parameters
                    port_num = len(tech.model[attr[2]]["ports"])
                    para_num_start = port_num + 3

                    # extracting device parameters
                    for i in range(para_num_start, len(attr)): 
                        info = attr[i]
                        tech.model[attr[2]][info.split("=")[0]] = info.split("=")[1]

        # start of layers
        elif re.match('layers',line):
            match = "layers"

        # start of units
        elif re.match('units',line):
            match = "units"

        # start of rules
        elif re.match('rules',line):
            match = "rules"

            # get rules name
            rules: str = re.search('rules\s+(\S+)',line).group(1)

        # start of models
        elif re.match('models',line):
            match = "models"

    file.close()    # close file


def technology_routing_layers(tech: Tech) -> int:
    """
    @brief: Get the total number of routing layers
    @param: tech -> technology object
    """
    count: int = 0
    for name in tech.layer:
        if "metal" in name or "poly" in name:
            count += 1

    return count


def read_netlist_file(tech: Tech, circuit: dict, filename: str) -> None:
    """
    @brief: Parse netlist file 
    @param: tech -> technology object
    @param: circuit -> circuit netlist (dictionary)
    @param: filename -> netlist file name
    """
    # check if the netlist file exists
    if not os.path.exists(filename):
        print("ERROR: Netlist file does not exist.")
        sys.exit()

    # check if the model file have been read
    if not tech.model:
        print("ERROR: Model file haven't read in. Netlist file can't be read.")
        return

    ### Stage 1: Get All Subckt Information ###
    file = open(filename, 'r')
    # read from file line by line
    for line in file:
        # if detect subckt header
        if re.match(".?subckt",line.lower()):     # .lower() for case-insensitive
            # get sub-circuit name
            name = re.search("\S+\s+(\S+)\s+",line).group(1)
            circuit[name] = Circuit(name)
            
            # get sub-circuit ports
            ports = re.search("\S+\s+\S+\s+(.+)\n",line).group(1).split()
            for net in ports:
                circuit[name].port[net] = Port(net)

    file.close()

    ### Stage 2: Get All Device Information ###
    match: str  = None          # match flag
    file = open(filename, 'r')  # open file
    # read from file line by line
    for line in file:
        # skip comment line and empty line
        if re.match(r'\s*\*',line) or re.match(r'\s*\n',line):
            continue

        # start extracting content
        if match == "subckt":
            # end of subckt
            if re.match('.?ends',line.lower()):     # .lower() for case-insensitive
                match = None

            # subckt definition is not closed
            elif re.match('.?subckt',line.lower()):
                print("ERROR: Subckt definition is not closed.")
                sys.exit()

            # extracting information (call function)
            else:
                device_extract(tech, circuit, circuit[name], line)                                            

        # if detect subckt header
        elif re.match(".?subckt",line.lower()):     # .lower() for case-insensitive
            match = "subckt"

            # get sub-circuit name
            name = re.search("\S+\s+(\S+)\s+",line).group(1)

    file.close()    # close file


def device_extract(tech: Tech, netlist: dict, circuit: Circuit, line: str) -> None:
    """
    @brief: Extract device information from netlist line
    @param: tech -> technology object
    @param: netlist -> full circuit netlist (dictionary)
    @param: circuit -> specific sub-circuit (circuit object)
    @param: line -> netlist line
    """
    # get device and sub-circuit list
    device: dict = circuit.device
    subckt: dict = circuit.subckt

    # trim sub-circuit line (for CDL format)
    trim_list: str = ["/", "$", "(", ")", "[", "]"]
    for trim in trim_list:
        line = line.replace(trim, "")
    
    # get attribute
    init: str = re.search(r'^(.)',line).group(1)   # get the first character
    attr: str = line.split()                       # get all attributes

    # extract Subckt
    if init == tech.model["subckt"]["init"]:
        # initialize sub-circuit
        subckt[attr[0]] = SubCkt(attr[0])

        # get sub-circuit information (name and nets connection)
        subckt[attr[0]].name = attr[-1]
        nets: str = re.search(r''+attr[0]+'\s+(.*)\s+'+attr[-1]+'',line).group(1).split()

        # get sub-circuit nodes
        subckt_in_netlist: Circuit = netlist[attr[-1]]          # get sub-circuit in the full netlist
        for i, port in enumerate(subckt_in_netlist.port):       # get sub-circuit port
            subckt[attr[0]].node[port] = Node(port, nets[i])    # assign sub-circuit node

        return

    # extract Device
    for name in tech.model:
        # check if the initial matched and model name are found in the attribute list
        if tech.model[name]["init"] == init and name in attr:
            # check if the device type is supported and initialize the device object
            if tech.model[name]["type"] in ["nmos", "pmos", "nfin", "pfin", "cap", "res", "diode"]:
                device[attr[0]] = Device(attr[0])
            else:
                print("ERROR: Unknown device type.")
                sys.exit()
            
            # get device basic information
            device[attr[0]].type = tech.model[name]["type"]
            device[attr[0]].name = name

            # get device nodes (based on model nodes)
            for i, port in enumerate(tech.model[name]["ports"]):
                device[attr[0]].node[port] = Node(port, attr[i+1])

            # get device parameters (based on model parameters)
            for para in tech.model[name]:
                if para not in ["init", "type", "ports"]:
                    device[attr[0]].param[para] = re.search(r''+tech.model[name][para]+'=(\S+)',line).group(1) if re.search(r''+tech.model[name][para]+'=\S+',line) else None
            
            return


def netlist_hierarchy(circuit: dict) -> list:
    """
    @brief: Get the hierarchy of the netlist
    @param: circuit -> circuit netlist (dictionary)
    """
    def dfs(circuit: dict, name: str, namelist: list) -> None:
        """
        @brief: Depth First Search (DFS) algorithm for netlist hierarchy
        @param: circuit -> circuit netlist (dictionary)
        @param: name -> circuit name
        @param: namelist -> list of circuit name
        """
        if name in namelist:
            return

        for subid in circuit[name].subckt:
            subname = circuit[name].subckt[subid].name
            dfs(circuit, subname, namelist)

        namelist.append(name)

    # get the hierarchy of the netlist
    namelist = []
    for name in circuit:
        dfs(circuit, name, namelist)

    return namelist


def read_constraint_file(circuit: dict, filename: str) -> None:
    """
    @brief: Parse layout constraint file 
    @param: circuit -> circuit object
    @param: filename -> layout constraint file name
    """
    # check if the layout constraint file exists
    if not os.path.exists(filename):
        print("ERROR: Layout constraint file does not exist.")
        sys.exit()

    # Read from file line by line
    match: str  = None
    file = open(filename, 'r')
    for line in file:
        # skip comment line and empty line
        if re.match(r'\s*\*',line) or re.match(r'\s*\n',line):
            continue

        # start extracting content
        if match:
            # end of extract
            if re.match('end',line):
                match = None

            # extracting information (call function)
            elif match == "constr":
                constraint_extract(circuit[name], line)    

            # extracting information (call function)
            elif match == "port":
                port_extract(circuit[name], line) 

        # start of constr
        elif re.match('constr',line):
            match = "constr"

            # get sub-circuit name
            name = re.search("\S+\s+(\S+)\s+",line).group(1)

            # get instance tap
            # tap = re.search("tap=(\S+)",line).group(1) if re.search("tap=\S+",line) else "None"

        # start of port
        elif re.match('port',line):
            match = "port"

            # get sub-circuit name
            name = re.search("\S+\s+(\S+)\s+",line).group(1)

    file.close()


def constraint_extract(circuit: Circuit, line: str) -> None:
    """
    @brief: Extract constraint information from constraint line
    @param: circuit -> circuit object
    @param: line -> constraint line in constraint file
    """
    # get group list for constraint
    group: dict = circuit.group

    # get attribute
    attr: str = line.split()

    # initialize group
    group[attr[0]] = Group(attr[0])     # add new group to group list
    current: Group = group[attr[0]]     # get current group

    # get group device list
    inst_list = attr[1].split(",")
    inst_type = []

    # Condition #1: check if the inst_list is the group list or not (#TODO)
    print("inst_list: ", inst_list)

    # Condition #2: check if the device instance exists in the netlist
    for inst in inst_list:
        if inst in circuit.device:
            device: Device = circuit.device[inst]
            inst_type.append(device.type)

        elif inst in circuit.subckt:
            subckt: SubCkt = circuit.subckt[inst]
            # print("INFO: Sub-circuit instance \"{}\" is found in \"{}\".".format(inst,circuit.name))

        else:
            print("ERROR: Device instance \"{}\" does not exist in \"{}\".".format(inst,circuit.name))
            sys.exit()

    # check if the device type is the same
    if len(set(inst_type)) == 0:
        # subckt instance
        current.type = "subckt"
 
        # assign subckt instance to group
        for inst in inst_list:
            current.inst.append(circuit.subckt[inst])

    elif len(set(inst_type)) == 1:
        # assign device type to group
        current.type = inst_type[0]

        # assign device instance to group
        for inst in inst_list:
            current.inst.append(circuit.device[inst])
    
    else:
        print("ERROR: Device type in the group is not the same.")
        print("ERROR: Group device \"{}\" types: {}".format(inst_list, inst_type))
        sys.exit()

    # get group constraint information
    current.constraint["mf_sym"] = re.search("mf_sym=(\S+)",line).group(1) if re.search("mf_sym=\S+",line) else "None"
    current.constraint["mp_sym"] = re.search("mp_sym=(\S+)",line).group(1) if re.search("mp_sym=\S+",line) else "None"
    current.constraint["mf_row"] = int(re.search("mf_row=(\S+)",line).group(1)) if re.search("mf_row=\S+",line) else 1
    current.constraint["mp_row"] = int(re.search("mp_row=(\S+)",line).group(1)) if re.search("mp_row=\S+",line) else 1
    current.constraint["dummy"] = re.search("dummy=(\S+)",line).group(1) if re.search("dummy=\S+",line) else "False"
    current.constraint["tap"] = re.search("tap=(\S+)",line).group(1) if re.search("tap=\S+",line) else "None"


def port_extract(circuit: Circuit, line: str) -> None:
    """
    @brief: Extract port information from port line
    @param: circuit -> circuit object
    @param: line -> port line in constraint file
    """
    # get port information
    ports = line.split()
    for port in ports:
        tmp = port.split("=")

        # check if the port exists in the netlist
        if tmp[0] in circuit.port:
            circuit.port[tmp[0]].position = tmp[1]
        else:
            print("ERROR: Port \"{}\" does not exist in \"{}\".".format(tmp[0],circuit.name))
            sys.exit()
        

def set_default_constraint(circuit: dict) -> None:
    """
    @brief: Set default constraint for device that is not in the constraint file
    """
    for name in circuit:
        # get instances list
        inst_list = []
        for gname in circuit[name].group:
            inst_list.extend([inst.id for inst in circuit[name].group[gname].inst])

        n = 1
        # get all devices in the netlist
        for dev in circuit[name].device:
            # check if the device instance is not in the constraint file
            if dev not in inst_list:
                # initialize group
                circuit[name].group["D"+str(n)] = Group()
                current: Group = circuit[name].group["D"+str(n)]

                # assign device instance to group
                current.inst.append(circuit[name].device[dev])

                # assign device type to group
                current.type = circuit[name].device[dev].type

                # set default constraint
                current.constraint["mf_sym"] = "None"
                current.constraint["mp_sym"] = "None"
                current.constraint["mf_row"] = 1
                current.constraint["mp_row"] = 1
                current.constraint["dummy"] = "False"
                current.constraint["tap"] = "None"

                n += 1
