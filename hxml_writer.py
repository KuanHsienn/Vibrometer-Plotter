#Code adapted from hxml_generation originally by Soon Hon

import numpy as np
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

class HXMLGenerator:
    def __init__(self, filename_hxml, re_arrange=True):
        self.filename_hxml = filename_hxml
        self.re_arrange = re_arrange
        self.hxml = None
        self.vCurveData = None

    def basic_structure(self):
        """Creates the basic structure of the HXML file."""
        with open(self.filename_hxml, "w", encoding="utf-8") as creatFile:
            pass  # Ensure the file is created or cleared

        self.hxml = ET.Element('hxml')
        head = ET.SubElement(self.hxml, 'head')
        docu = ET.SubElement(head, 'Document')
        datVersion = ET.SubElement(docu, 'DataVersion')
        datType = ET.SubElement(docu, 'DataType')
        ldocNode = ET.SubElement(docu, 'LDocNode')
        platformVer = ET.SubElement(docu, 'PlatformVersion')

        data = ET.SubElement(self.hxml, 'data')
        dataSet = ET.SubElement(data, 'dataset')
        ET.SubElement(dataSet, 'longDataSetDesc')
        ET.SubElement(dataSet, 'shortDataSetDesc')
        ET.SubElement(dataSet, 'acpEarhookType')
        self.vCurveData = ET.SubElement(dataSet, 'v-curvedata')

        ET.SubElement(self.hxml, 'environment')

        # Fill header elements with information
        datVersion.text = '0.0.0.1'
        datVersion.set("XsdVersion", "0.0.0.1")
        datType.text = "hiCurve"
        ldocNode.text = "//hxml/data"
        platformVer.text = "n.a."

        tree = ET.ElementTree(self.hxml)
        tree.write(self.filename_hxml, encoding="UTF-8", xml_declaration=True)

        if self.re_arrange:
            self.re_arrange_file()

    def re_arrange_file(self):
        """Pretty-prints the XML file."""
        with open(self.filename_hxml, "r") as xml_file:
            xml_content = xml_file.read()

        dom = minidom.parseString(xml_content)
        pretty_xml = dom.toprettyxml()

        with open(self.filename_hxml, "w") as formatted_file:
            formatted_file.write(pretty_xml)

    def graphs_to_hxml(self, graphs_list, remarks_list = None):
        """Populates the HXML file with data from a dictionary."""
        self.basic_structure()

        #no remarks
        if remarks_list is None:

            for graph in graphs_list:
                np.set_printoptions(linewidth=np.inf, precision=2, floatmode="fixed")
                
                #once i changed f to Frequency and Response_Magnitude to velocity and the units as well, rdstarter cant display it
                self.new_field_hxml(graph.plot_title, self.vCurveData, "f", graph.x_label_unit, np.array(graph.x_data), graph.y_label, graph.y_label_unit, np.array(graph.y_data), "No remarks")


        #there are remarks
        else: 
            #initialise counter to access remark in remarks_list
            counter = 0

            for graph in graphs_list:
                np.set_printoptions(linewidth=np.inf, precision=2, floatmode="fixed")
                
                #once i changed f to Frequency and Response_Magnitude to velocity and the units as well, rdstarter cant display it
                self.new_field_hxml(graph.plot_title, self.vCurveData, "f", graph.x_label_unit, np.array(graph.x_data), graph.y_label, graph.y_label_unit, np.array(graph.y_data), remarks_list[counter])
                
                #increment counter
                counter += 1


        tree = ET.ElementTree(self.hxml)
        tree.write(self.filename_hxml, encoding="UTF-8", xml_declaration=True)

        if self.re_arrange:
            self.re_arrange_file()

    def excel_to_hxml(self, data_dicts):
        """Populates the HXML file with data from a dictionary."""
        self.basic_structure()
        number_of_curves = len(data_dicts)

        for i in range(number_of_curves):
            np.set_printoptions(linewidth=np.inf, precision=2, floatmode="fixed")

            freq = np.array(data_dicts[i]["frequency"])
            resp = np.array(data_dicts[i]["response_magnitude"])
            curvenaming = data_dicts[i]["curvename"]

            self.new_field_hxml(curvenaming, self.vCurveData, "f", "Hz", freq, "Response_Magnitude", "dBSPL/V", resp)

        tree = ET.ElementTree(self.hxml)
        tree.write(self.filename_hxml, encoding="UTF-8", xml_declaration=True)

        if self.re_arrange:
            self.re_arrange_file()

    def new_field_hxml(self, curve_name, par_node, curv1_size, curv1_unit, curv1_values, curv2_size, curv2_unit, curv2_values, remarks):
        """Adds a new field to the HXML file."""
        curve_data = ET.SubElement(par_node, 'curvedata')
        ET.SubElement(curve_data, 'longDataSetDesc')
        ET.SubElement(curve_data, 'shortDataSetDesc')

        curve_data.set("CurveDataName", curve_name)

        self.insert_one_curve_hxml(curve_data, curv1_size, curv1_unit, curv1_values)
        self.insert_one_curve_hxml(curve_data, curv2_size, curv2_unit, curv2_values)
        self.insert_one_curve_metadata_hxml(curve_data, remarks)

    def insert_one_curve_hxml(self, par_node, curv_size, curv_unit, curv_values):
        """Inserts a single curve into the HXML file."""
        curve = ET.SubElement(par_node, 'curve')
        curve.set("name", curv_size)
        curve.set("unit", curv_unit)

        if isinstance(curv_values, (np.ndarray, np.generic)):
            curve.text = "[" + ' '.join(map(str, curv_values)) + "]"
        else:
            curve.text = curv_values

    def insert_one_curve_metadata_hxml(self, par_node, remarks):
        """Inserts a single remark line into the HXML file."""
        curve = ET.SubElement(par_node, 'curve')
        curve.set("name", "remarks")
        curve.set("unit", "")

        curve.text = remarks


