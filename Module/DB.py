import sys
import os
import re

class Design:
    """
    @brief: Design Class
    @param: name -> design name
    """
    def __init__(self, name: str = "") -> None:
        self.name: str = name
        self.tech: Tech = Tech()
        self.circuit: dict = {}


class Tech:
    """
    @brief: Technology class
    """
    def __init__(self) -> None:
        # technology layers information 
        self.layer: dict = {}

        # technology physical unit (db) and logical unit (user) 
        self.unit: dict = {"db" : 1e-9, "user" : 1}

        # technology physical design rules 
        self.min_width_rule: dict = {}
        self.min_size_rule: dict  = {}
        self.min_area_rule: dict  = {}
        self.min_spacing_rule: dict = {}
        self.min_enclosure_rule: dict = {}
        self.min_extension_rule: dict = {}

        # technology model parameters
        self.model: dict = {}


class Layer:
    """
    @brief: Technology layer class
    @param: gds -> gds layer number
    @param: datatype -> gds datatype number
    """
    def __init__(self, name: str, gds: str, datatype: str) -> None:
        # technology gds and datatype number
        self.name: str = name
        self.gds: int = int(gds)
        self.datatype: int = int(datatype)


class Circuit:
    """
    @brief: Circuit class
    """
    def __init__(self, name: str="") -> None:
        # circuit netlist information
        self.name: str = name
        self.port: dict = {}
        self.device: dict = {}
        self.subckt: dict = {}

        # circuit instance information
        self.group: dict = {}

        # circuit layout information
        self.width: float = 0
        self.height: float = 0


class Port:
    """
    @brief: Circuit Port Class
    @param: name -> port name
    """
    def __init__(self, name: str="") -> None:
        # port information
        self.name: str = name
        self.position: str = ""
        self.location: list = [0,0]
        self.layer: str = ""
        self.shape: dict = {}


class Pin:
    """
    @brief: Layout Pin class
    """
    def __init__(self, net: str, layer: str, pt1: list=[0,0], pt2: list=[0,0]) -> None:
        # pin information
        self.net: str = net  
        self.layer: str = layer
        self.pt1: list = [pt1[0], pt1[1]]
        self.pt2: list = [pt2[0], pt2[1]]


class Device:
    """
    @brief: Device Instance class
    @param: idnum -> device id 
    """
    def __init__(self, idnum: str="") -> None:
        # device information
        self.id: str = idnum
        self.name: str = ""
        self.type: str = ""
    
        # device node connection
        self.node: dict = {}

        # device parameters
        self.param: dict = {}


class SubCkt:
    """
    @brief: Sub Circuit Instance class
    @param: idnum -> subckt id 
    """
    def __init__(self, idnum: str="") -> None:
        # subckt information
        self.id: str = idnum
        self.name: str = ""

        # subckt node connection
        self.node: dict = {}

        # subckt parameters
        self.param: dict = {}

class Group:
    """
    @brief: Group Instance class
    @param: idnum -> group id 
    """
    def __init__(self, idnum: str="") -> None:
        # group information
        self.id: str = idnum
        self.type: str = ""
        self.inst: list = []

        # group contraints and topology
        self.constraint: dict = {}
        self.topology: dict = {}

        # group layout information
        self.shape: dict = {}
        self.boundary: Box = None
        self.pin: list = []


class Node:
    """
    @brief: Device and Sub Circuit Node class
    @param: net -> node connection net name
    @param: type -> node type
    """
    def __init__(self, type: str, net: str) -> None:
        # node information
        self.type: str = type
        self.net: str  = net

        # node parameter
        self.param: dict = {}


class Box:
    """
    @brief: Layout Shape Box class
    @param: layer -> layer name
    @param: pt1 -> lower left point
    @param: pt2 -> upper right point
    """
    def __init__(self, layer: str, pt1: list=[0,0], pt2: list=[0,0]) -> None:
        # shape information
        self.layer: str = layer
        self.x: list = [pt1[0], pt2[0]]
        self.y: list = [pt1[1], pt2[1]]
        
        self.width: float  = pt2[0] - pt1[0]
        self.height: float = pt2[1] - pt1[1]


class Polygon:
    """
    @brief: Layout Shape Polygon class
    @param: layer -> layer name
    @param: pts -> polygon points
    """
    def __init__(self, layer: str, pts: list) -> None:
        # shape information
        self.layer: str = layer
        self.pts: list = pts


class Text:
    """
    @brief: Layout Shape Text class
    @param: layer -> layer name
    @param: pt -> text position
    @param: text -> text string
    """
    def __init__(self, layer: str, pt: list=[0,0], text: str="") -> None:
        # shape information
        self.layer: str = layer
        self.x: float = pt[0]
        self.y: float = pt[1]
        
        self.text: str = text


class SRef:
    """
    @brief: Layout Shape SRef class
    @param: cell -> cell name
    @param: pt -> cell position
    """
    def __init__(self, cell: str, pt: list=[0,0]) -> None:
        # shape information
        self.cell: str = cell
        self.x: float = pt[0]
        self.y: float = pt[1]