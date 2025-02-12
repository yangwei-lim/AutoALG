from Module import DB

from gdsii.library import Library
from gdsii.structure import Structure
from gdsii.elements import *

def write_gds_file(tech: DB.Tech, circuit: dict, filename: str, path: str) -> None:
    """
    @brief: save the layout to GDS file
    @param: tech -> technology object
    @param: circuit -> circuit netlist (dictionary)
    @param: filename -> output file name
    """
    # layout library: version, filename, unit
    library = Library(5, filename.encode('UTF-8'), tech.unit['db']*tech.unit['user'], tech.unit['user'])

    # get each circuits
    for name in circuit:
        # initialize structure with the name as the circuit name
        struct  = Structure(name.encode('UTF-8'))

        # get each group of instances
        for inst in circuit[name].group:
            current = circuit[name].group[inst]

            # get each layers name in the group
            for layer in current.shape:
                # get all the shapes
                for shape in current.shape[layer]:
                    # shape type is a rectangle
                    if isinstance(shape, DB.Box):
                        # rectangle information: gds, datatype, coordinates
                        boundary = Boundary(tech.layer[layer].gds,tech.layer[layer].datatype,
                                    [(round(shape.x[0]/tech.unit['user']), round(shape.y[0]/tech.unit['user'])),
                                     (round(shape.x[0]/tech.unit['user']), round(shape.y[1]/tech.unit['user'])),
                                     (round(shape.x[1]/tech.unit['user']), round(shape.y[1]/tech.unit['user'])),
                                     (round(shape.x[1]/tech.unit['user']), round(shape.y[0]/tech.unit['user'])),
                                     (round(shape.x[0]/tech.unit['user']), round(shape.y[0]/tech.unit['user']))]
                                    )
                        struct.append(boundary)
                        # print(shape.x[0]/tech.unit['user'], shape.y[0]/tech.unit['user'], shape.x[1]/tech.unit['user'], shape.y[1]/tech.unit['user'])

                    # shape type is a text
                    elif isinstance(shape, DB.Text):
                        # text information: gds, datatype, coordinates, text
                        text = Text(tech.layer[layer].gds,tech.layer[layer].datatype,
                                    [(round(shape.x/tech.unit['user']), round(shape.y/tech.unit['user']))],
                                    shape.text.encode('UTF-8'))
                        text.strans = int(0b0000)             # text transformation = no transformation
                        text.mag = 0.05                       # text size = 0.05
                        text.presentation = int(0b000101)     # text presentation
                        struct.append(text)

                    # shape type is a sref
                    elif isinstance(shape, DB.SRef):
                        # sref information: gds, datatype, coordinates, reference
                        sref = SRef(shape.cell.encode('UTF-8'),
                                    [(round(shape.x/tech.unit['user']), round(shape.y/tech.unit['user']))])
                        sref.strans = int(0b0000)            # sref transformation = no transformation
                        struct.append(sref)

        # get each port in the circuit
        for net in circuit[name].port:
            # get each layers name in the port
            for layer in circuit[name].port[net].shape:
                # get all the shapes
                for shape in circuit[name].port[net].shape[layer]:
                    if isinstance(shape, DB.Box):
                        # rectangle information: gds, datatype, coordinates
                        boundary = Boundary(tech.layer[layer].gds,tech.layer[layer].datatype,
                                    [(round(shape.x[0]/tech.unit['user']), round(shape.y[0]/tech.unit['user'])),
                                     (round(shape.x[0]/tech.unit['user']), round(shape.y[1]/tech.unit['user'])),
                                     (round(shape.x[1]/tech.unit['user']), round(shape.y[1]/tech.unit['user'])),
                                     (round(shape.x[1]/tech.unit['user']), round(shape.y[0]/tech.unit['user'])),
                                     (round(shape.x[0]/tech.unit['user']), round(shape.y[0]/tech.unit['user']))]
                                    )
                        struct.append(boundary)
                        # print(shape.x[0]/tech.unit['user'], shape.y[0]/tech.unit['user'], shape.x[1]/tech.unit['user'], shape.y[1]/tech.unit['user'])

                    if isinstance(shape, DB.Text):
                        # text information: gds, datatype, coordinates, text
                        # print(round(shape.x/tech.unit['user']), round(shape.y/tech.unit['user']), shape.text)
                        text = Text(tech.layer[layer].gds,tech.layer[layer].datatype,
                                    [(round(shape.x/tech.unit['user']), round(shape.y/tech.unit['user']))],
                                    shape.text.encode('UTF-8'))
                        text.strans = int(0b0000)
                        text.mag = 0.05
                        text.presentation = int(0b000101)
                        struct.append(text)

        # append the structure to the library
        library.append(struct)

    # save the library to GDS file
    stream = open(path+"/"+filename, "wb")
    library.save(stream)