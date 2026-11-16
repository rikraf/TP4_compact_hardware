import os
import sys
from xml.dom import minidom
from xml.dom.minidom import parse, parseString
import libxml2
import fileinput
import os.path, time
from ctypes import *
import string
import optparse


##COMMENTS:
## Need to change the position of where the calibration data is inserted... should be area 1.
## Need to check all type len bytes
## Need to check the common header generation
## Check that the checksums are correct
## Check that the multirecord headers are correct
## Change things so that calib data file can contain whitespace after comma


default_inputFile = './eeprom_input.xml'



########################################
# Define New Type
########################################

type_list =["yes_no","calib_data"]

type_list_description = [" Takes an input of the form 'yes' or 'no', returns an associated number","This is the type conversation for calibration data,\n should not be used in the XML file"]




########################################
# Functions
########################################

multi_record_options = ["power_supply_information","DC_OUTPUT","DC_LOAD","management_access_record","base_compatibility_record","extended_compatibility_record","OEM_record"]


def yes_no_function(string):
        if string.lower() =="yes":
                return ["00000001"]
        elif string.lower()=="no":
                return ["00000000"]
        else:
                print "Content not as expected for type 'yes_no'"
                print "Expected 'yes' or 'no'"
                return "error"


def generate_addresses(data_size):
    address_list =[]
    for i in range(data_size):
    	address_bytes = convert_to_byte(i,2)
    	combined_addr = address_bytes[0]+address_bytes[1]

        address_list.append([combined_addr])
    return address_list


def print_area_nums():
    print "\nThe 'number' attribute in 'Area' elements in the XML file must correspond to the type of area"
    print "The type options and their corresponding numbers are shown below :"

    areas=["internal use" ,"chassis info" ,"board info","product info","multi area"]
    print ""
    for i in range(len(areas)):
        print "%d  : %s"%((i+1),areas[i])
    print ""


def print_type_options():
        print "type options"
        print "\nascii : Enter any text\n"
        print "binary  : Enter in the form \"00000000\" , ie grouped in 8 bis"
        print "          For more than 8 bits write as 00000000 00000000\n"
        print "BCD  : Enter an integer\n"
        print "Signed_short  : Enter in the form +0.00 or -0.00"
        print "                To be given in 0.01 incriments\n"

        if len(type_list)!=0:
                for i in range(len(type_list)):
                        print type_list[i] + "  :" + type_list_description[i]+"\n"


def convert_to_byte(number,num=0):

    converted=[]
    separate_bytes=[]
    character = bin(number)[2:]

    if num == 0:
    	required_length = (len(character)/9 +1)*8
    else:
    	required_length = num*8

    converted.append(('0' * (required_length-len(character))) + character)
    (required_length/8)
    for i in range(required_length/8):
        separate_bytes.append(converted[0][((i+1)*8)-8:(i+1)*8])
    return separate_bytes



def generate_multirecord_header(mh_type,last_multirecord, length):
    header=[]
    if mh_type==multi_record_options[0] :
        type_identifier="00000000"
    elif mh_type==multi_record_options[1]:
        type_identifier="00000001"
    elif mh_type==multi_record_options[2]:
        type_identifier="00000010"
    elif mh_type==multi_record_options[3]:
        type_identifier="00000011"
    elif mh_type==multi_record_options[4]:
        type_identifier="00000100"
    elif mh_type==multi_record_options[5]:
        type_identifier="00000101"
    elif mh_type==multi_record_options[6]:
        type_identifier="11111111"
    else:
        print "unidentified record type"
        type_identifier = "WRONG mh type"

    if last_multirecord =='yes':
        record_field = convert_to_byte(130)
    else:
        record_field = convert_to_byte(2)

    header.append([type_identifier])
    header.append(record_field)
    header.append([str(convert_to_byte(length)[0])])
    mrchecksum = return_checksum(length)
    header.append([str(mrchecksum)])
    header.append(["11111011"])
    return header



def append_sections(master_data,common_header):
    master_binary =[]

    for bytes in common_header:
        master_binary.append(bytes)

##    for i in range(len(master_data)):
##        for j in range(len(master_data[i])):
##            #print master_data[i]
##
##            if len(master_data[i][j])>1:
##                for k in range(len(master_data[i][j])):
##                    master_binary.append([master_data[i][j][k]])
##
##            else:
##                master_binary.append(master_data[i][j])

    for area in range(len(master_data)):
            for content in range(len(master_data[area])):
                for inside in range(len(master_data[area][content])):
                    if  type(master_data[area][content][inside])==list:
                        for further in range(len(master_data[area][content][inside])):
                            master_binary.append([master_data[area][content][inside][further]])
##                            print master_data[area][content][inside][further]
                    else:
                        master_binary.append([master_data[area][content][inside]])
##                        print master_data[area][content][inside]
    return master_binary


def append_common_header(areas_found,area_lengths):
    offset = [0,0,0,0,0]
    array  = [0,0,0,0,0]
    for i in range(len(areas_found)):
        array[int(areas_found[i])-1]=area_lengths[i]
    common_header = []
    common_header.append([str(convert_to_byte(1)[0])])
    for i in range(len(array)):
        if int(array[i])==0:
            common_header.append(convert_to_byte(0))
        else:
            common_header.append(convert_to_byte(sum(array[0:i])+1))

    common_header.append(["00000000"])
    common_header.append(["11110000"])  # CHECK THIS
    return common_header



def gen_common_header_tags():
        tags = []
        tags.append(["Identifier"])
        tags.append(["Offset to area 1"])
        tags.append(["Offset to area 2"])
        tags.append(["Offset to area 3"])
        tags.append(["Offset to area 4"])
        tags.append(["Offset to area 5"])
        tags.append(["Padding for Common Header"])
        tags.append(["Common header checksum"])
        return tags



def write_to_file(file_name,data_list,addr_list,tag_bytes,debug):

    if file_name ==None:
        writing_to_file=open("eeprom_formatted_data.txt","w")
    else:
        writing_to_file=open(file_name,"w")

    if len(data_list)!=len(addr_list):
        print "problem with data and addr length"


    if debug:
        for h in range(len(data_list)):
                writing_to_file.write("%s       %s      %s\n"%(addr_list[h][0],data_list[h][0],tag_bytes[h][0]))

               # print ("%s       %s      %s \n"%(addr_list[h][0],data_list[h][0],tag_bytes[h][0]))
    else:
        for h in range(len(data_list)):
                writing_to_file.write("%s       %s \n"%(addr_list[h][0],data_list[h][0]))

                #print ("%s       %s      %s \n"%(addr_list[h][0],data_list[h][0],tag_bytes[h][0]))


    if file_name ==None:
        print "Formatted data written to 'EEPROM_FORMATTED_DATA.txt' : in current directory"
    else:
        print "Formatted data written to '",file_name,"' : in current directory"
    return 0


def return_checksum(byte):
    binary_value=bin(byte%256)[2:]
    eight_bit_length=str(('0' * (8- len(binary_value))) + binary_value  )
    inv_binary_value =[]
    for h in eight_bit_length:
        if h=='0':
            inv_binary_value.append('1')
        elif h=='1':
            inv_binary_value.append('0')
    inverted="".join(element for element in inv_binary_value)
    twos_comp_checksum = (bin(int(inverted,2)+1)[2:])
    return twos_comp_checksum


def convert_to_ascii(text):
    converted_line=[]
    for word in text:
        for char in word:
            character=bin(ord(char))[2:]
            converted_line.append(('0' * (8-len(character))) + character)
 #   print  "ascii converted",converted_line
    return converted_line


def convert_to_bcd(text):
    bcd_conv=[]
    if text.isdigit()!=True:
        print "Error : BCD value contains a character, ensure the content contains only numbers"
        return "error"
    if len(text.split())!=1:
        print "Error : BCD value not entered correctly"
        print "Ensure there is no whitespace between characters"
        return "error"
    for letter in text:
        number=int(letter)
        bcd_num=bin(number)[2:]
        bcd_conv.append(('0' * (8 - len(bcd_num))) + bcd_num)
  #  print "BCD", bcd_conv
    return bcd_conv


def print_calib_info():
    print "\nCalibration data should be stored in a file in the following format:"
    print "[hex number],[yes/no]"
    print "E.g. 0xABCD,yes"
    print "The hex number must start with 0x"
    print "If a typelen byte is desired for the data, write yes, else no"


def print_multi_record_options():
    print "\nPlease use one of the following MultiRecord names:"
    for i in range(len(multi_record_options)):
        print multi_record_options[i]
    return 0


def convert_to_signed_short(content):
    if len(content)<=1:
        print " Signed short input not as expected"
        print " Please give in the for +0.00 or -0.00"
        return "error"
    sign = content[0]
    fp_value =float(content[1:])
    converted_ss=[]
    value=int(fp_value*100)
    if sign=="+":
        binary_value=bin(value)[2:]
        sixteen_bits=str(('0' * (16- len(binary_value))) + binary_value)
        sixteen_bits,"sixteen"
        if sixteen_bits[0]==1:
            print "NUMBER IS TOO BIG"
        converted_ss.append(sixteen_bits[0:8])
        converted_ss.append(sixteen_bits[8:16])
        #return converted_ss
    elif sign=="-":
        converted_ss=[]
        inv_binary_value=[]
        binary_value=bin(value)[2:]
        sixteen_bits=str(('0' * (16- len(binary_value))) + binary_value)
        for h in sixteen_bits:
            if h=='0':
                inv_binary_value.append('1')
            elif h=='1':
                inv_binary_value.append('0')
        inverted="".join(element for element in inv_binary_value)
        twos_comp=bin(int(inverted,2)+1)[2:]
        converted_ss.append(twos_comp[0:8])
        converted_ss.append(twos_comp[8:16])
        #print converted_ss,"converted SS"
    else:
        print"Error : Input for signed short in wrong format"
        print"Expected format - +0.00  or -0.00"
        print"Give input in 10mV/mA incriments"
        return "error"

   # print "converted ss", converted_ss
    return converted_ss


def convert_to_6bit_ascii(text):
    print "6bit packed ascii currently not supported."
    return "error"


def check_byte_size(text):
    array =[]
    bytes_split =text.split()
    for i in range(len(bytes_split)):
        if len(bytes_split[i])!=8:
            print "Binary input not in byte size "
            print "If two or more bytes - enter in the form  - \"Byte1 Byte2\""
            return "error"
        else:
            array.append(bytes_split[i])
    return array


def type_length_byte(type_enc,length):          #  allows the generation of a type length byte  Where is signed short?!
    #if type_enc=="ascii":
    array =[]
    field_size = []
    type_len_byte=['0','0','0','0','0','0','0','0']
    binary_len=bin(length)[2:]
    field_size.append(('0' * (6-len(binary_len))) + binary_len)
    if type_enc== "ascii":
        type_len_byte[7]='1'
        type_len_byte[6]='1'
    elif type_enc=="bcd":
        type_len_byte[7]='0'
        type_len_byte[6]='1'
    elif type_enc in type_list or type_enc== "binary" or type_enc == "signed_short":
        type_len_byte[7]='0'
        type_len_byte[6]='0'
    else:
        print "Unrecognised conversion type"
        print "If necessary... add a function as described in \"fmc_eeprom_gen\" document"
        return "error"
        type_len_byte[7]='0'
        type_len_byte[6]='0'

    test_type_len = str(type_len_byte[7]) + str(type_len_byte[6]) + str(field_size[0])
    return [test_type_len]




def generate_tags(converted_line, data_type, area_num):
        tag_array=[]


        for fields in converted_line:
                #print fields
                #print data_type
                tag_array.append("Area Number :" + area_num + " Data Type :" + data_type )
        #print tag_array
        return tag_array
        #print converted_line


def gen_multi_record_header_tags():
        tags = []
        tags.append(["Multirecord Header : Record ID Type"])
        tags.append(["Multirecord Header : Format Version (Bit 7: Last MultiRecord Flag)"])
        tags.append(["Multirecord Header : Record Length"])
        tags.append(["Multirecord Header : Record Checksum"])
        tags.append(["Multirecord Header : Header Checksum"])
        return tags



def format_calib_data(hex_calib_data):
	#print int(hex_calib_data,16)
	#print convert_to_byte(int(hex_calib_data,16))
	return convert_to_byte(int(hex_calib_data,16))



def calibration_data(calibration_file):
	split_line =[]
	area_1_data=[]
	area_1_tags=[]
	area_1_data.append(["00000001"])
	area_1_tags.append(["The start of area 2"])



	f = open(calibration_file[0])
	for line in f:
		split_line = (line.split(','))

		converted_line = typeConvFunctionsMap["calib_data"](split_line[0])
		tags = generate_tags(converted_line,"calib_data", "2")

        	has_typelen = split_line[1].strip("\n")
        	if has_typelen.lower() =="yes":
        		type_len=type_length_byte("calib_data",len(converted_line))
                	area_1_data.append(type_len)
                	area_1_tags.append(["type_len byte"])
                area_1_data.append(converted_line)
                area_1_tags.append(tags)
	byte_count = []
	for fields in area_1_data:
        	for byte in fields:
                	byte_count.append(byte)

	area_len = len(byte_count)

	#print (len(byte_count)%8)
	while area_len%8!=7:
		area_1_data.append(["00000000"])
		area_1_tags.append(["Padding - in calibration area"])
		area_len = area_len +1



	area_1_data.append(["11000001"])
	area_1_tags.append(["End of fields identifier in calibration data area"])
	byte_count.append("anything")

	#print "byte count calib area", len(byte_count)


	length_calced = (area_len+1)/8
	return_area = [0,0,0]
	return_area[0] = area_1_data
	return_area[1] = area_1_tags
	return_area[2] = length_calced
	return return_area

#########################################
# Funtions map
#########################################
typeConvFunctionsMap = {
    'ascii'             : convert_to_ascii,
    'bcd'               : convert_to_bcd,
    'signed_short'      : convert_to_signed_short,
    'binary'            : check_byte_size,
    "yes_no"            : yes_no_function,
    "calib_data"	: format_calib_data
}

#########################################
# Parameters
########################################
##inputFile = './eeprom_input.xml'

#default_inputFile = './test.xml'


def main(file_name,input_name,debug,calibration_file):

    if input_name == None:
        doc = libxml2.parseFile(default_inputFile)

    elif len(input_name.split())==1:
        doc = libxml2.parseFile('./' + str(input_name.split()[0]))

    else:
        print "\n\nunexpected input for input file name"
        print "expected : filename.xml\n\n"

    error_count = 0
    master_data = []
    master_tags = []
    pos_of_area_len = 2
    data=[]
    addr=[]
    root = doc.getRootElement()
    memory_size = int(root.prop('memory_size'))
    area = root.children
    areas_found = []
    area_length =[]
    concat=[]


########################################################################################################################
# Loop through XML FILE
########################################################################################################################
    while area is not None:
        if area.type == "element":
            areas_found.append(area.prop('number'))
            area_data =[]
            area_tags =[]
            byte_count=[]
            pos_of_len_field = area.prop('pos_of_len_field')
            areaContent = area.children

            while areaContent is not None:
                if areaContent.type == "element":
                    areaContentName = areaContent.name                           ########################################
                    if (areaContentName!='multirecord'):                         # if fields, then process
                        field_name      = areaContent.prop('name')               ########################################
                        has_typelen     = areaContent.prop('has_typelen')
                        field_content   = areaContent.prop('content')
                        type            = areaContent.prop('type')
                        ########################################
                        # Within Area
                        ########################################
                        if typeConvFunctionsMap.has_key(type):
                                converted_line = typeConvFunctionsMap[type](field_content)
                                tags = generate_tags(converted_line,type, area.prop('number'))
                        # add descripter

                        else:
                                converted_line = "error"
                                print "Type not contained in function map..."
                                print "If a new type is required, see \"fmc_eeprom_gen\" for details of how to add a new type"



                        if converted_line =="error":
                            print "ERROR Position : Area :",area.prop('number')," \'",areaContent.prop('name'),"\'"
                            error_count = error_count +1

                        if has_typelen == "yes":
                            type_len=type_length_byte(type,len(converted_line))

                            if type_len =="error":
                                print "Type len error"
                                print "ERROR Position : Area :",area.prop('number')," \'",areaContent.prop('name'),"\'"
                                error_count = error_count +1

                            area_data.append(type_len)
                            area_tags.append(["type_len byte"])

                        area_data.append(converted_line)
                        area_tags.append(tags)
                        ########################################################### Here


                                                                                ########################################
                    else:                                                       # else, go further to multirecord
                                                                                # nested loop within areas loop
                        ########################################                ########################################
                        # Next Child element - MultiRecord
                        ########################################
                        field = areaContent.children
                        multi_area_data =[]
                        multi_area_tags =[]
                        while field is not None:
                            if field.type=="element":
                                fieldContentName = field.name                   ########################################
                                if fieldContentName!='byteField':               # if fields, then process
                                    field_name =  field.prop('name')            ########################################
                                    has_typelen = field.prop('has_typelen')
                                    field_content = field.prop('content')
                                    type = field.prop('type')

                                    if typeConvFunctionsMap.has_key(type):
                                        converted_line = typeConvFunctionsMap[type](field_content)

                                        ##################################
                                        tags = generate_tags(converted_line,type,area.prop('number'))

                                        ##################################

                                    else:
                                        converted_line = "error"
                                        print "Type not contained in function map..."
                                        print "If a new type is required, see \"fmc_eeprom_gen\" for details"
                                        print "on how to add a new type"

                                    if converted_line == "error":
                                        print "ERROR Position :", areaContent.prop('name'),", Multirecord number: ",areaContent.prop('multi_record_num'),  " \'",field.prop('name'),"\'"
                                        error_count = error_count +1

                                    if has_typelen == "yes":
                                        type_len=type_length_byte(type,len(converted_line))
                                        if type_len =="error":
                                                print "Type len error"
                                                print "ERROR Position :", areaContent.prop('name'),", Multirecord number: ",areaContent.prop('multi_record_num'),  " \'",field.prop('name'),"\'"
                                                error_count = error_count +1


                                        multi_area_data.append(type_len)
                                        multi_area_tags.append(["type_len"])

                                    multi_area_data.append(converted_line)
                                    multi_area_tags.append(tags)
                                    ########################################################### Here



                                ########################################
                                # Next Child Element - ByteField Data
                                # Process ByteField
                                # Append to MultiRecord Data
                                ########################################        ########################################
                                else:                                           # else, go further to bytefield
                                    bytefieldData =[]                           # nested loop within multirecord loop
                                    bytefield = field.children                  ########################################
                                    while bytefield is not None:
                                        if bytefield.type=="element":
                                            bytefieldData.append(bytefield.prop('content'))
                                        bytefield = bytefield.next
                                    if len("".join(bytefieldData))!=8:
                                        print "ERROR : fields in byteField  \'",field.prop('name'),"\'  do not add to 8 bits"
                                        error_count = error_count +1
                                    multi_area_data.append(["".join(bytefieldData)])
                                    multi_area_tags.append(["bytefield"])
                                    bytefieldData=[]
                            field=field.next

                        ########################################
                        # Process MultiRecord data
                        # Append to Area Data
                        ########################################
                        for fields in multi_area_data:
                            for byte in fields:
                                byte_count.append(byte)
                        multi_record_header = generate_multirecord_header(areaContent.prop('name'),areaContent.prop('last_multirecord'),len(byte_count))
                        multi_record_header_tags = gen_multi_record_header_tags()

                        #master_data.append(multi_record_header)
                        #master_tags.append(multi_record_header_tags)
                        #area_data.append(multi_record_header)


                        #master_data.append(multi_area_data)
                        #area_data.append(multi_area_data)
                        #master_tags.append(multi_area_tags)

                        # New system
                        area_data.append(multi_record_header + multi_area_data)
                        area_tags.append(multi_record_header_tags + multi_area_tags)



                        byte_count=[]

                ########################################
                # Process Area fields
                # Append to master data
                ########################################
                areaContent = areaContent.next
            if (areaContentName!='multirecord'):
                area_data.append([convert_to_byte(int("C1",16))[0] ])
                area_tags.append(["END OF FIELDS IDENTIFIER"])
                for fields in area_data:
                    for byte in fields:
                        byte_count.append(byte)

                area_size = len(byte_count)

                if int(pos_of_len_field) == 0:
                    pad_size = 7
                    length_calc_addition = 1
                else:
                    length_calc_addition = 2
                    pad_size = 6

                #while len(byte_count)%8!=pad_size:
                while area_size%8!=pad_size:
		    area_size = area_size +1
                    area_data.append(["00000000"])
                    area_tags.append(["Padding to round to multiple of 8 byes"])
                #    byte_count.append(["00000000"])



             #  print "pos_of_len_field  :",pos_of_len_field
                #length_calced = (len(byte_count)+length_calc_addition)/8
                length_calced = (area_size+length_calc_addition)/8


                if int(pos_of_len_field) !=0:
                    area_data.insert(int(pos_of_len_field)-1,[convert_to_byte(length_calced)[0]])
                    area_tags.insert(int(pos_of_len_field)-1,["length of area " + area.prop('number')+" (multiples of 8bytes)"])
                area_length.append(length_calced)
                checksum =  return_checksum(int(length_calced))
                string =  checksum
                area_data.append([string])
                area_tags.append(["checksum"])

                #byte_count.append("doesnt matter")
                #byte_count.append("doesnt matter")
                master_data.append(area_data)
                master_tags.append(area_tags)

            ########################################
            # If multirecod, just give length as 1
            # Not important as offset is to start of
            # multi record area.
            ########################################
            else:
                master_data.append(area_data)
                master_tags.append(area_tags)
                area_length.append(1)
        area = area.next


    ### Process calibration data.

    if len(calibration_file)!=0:
    	area_1_info = calibration_data(calibration_file)
	area_1_data = area_1_info[0]
	area_1_tags = area_1_info[1]
	area_1_length = area_1_info[2]

	# need to change this to insert calibration data at offset 0
	#print areas_found
	#print area_length

	#print area_1_info[2]
	areas_found.insert(0,"1")
	area_length.insert(0,area_1_length)
	master_data.insert(0,area_1_data)
	master_tags.insert(0,area_1_tags)

	#print areas_found
	#print area_length
	#areas_found.insert(1,"1")
	#area_length.insert(1,area_1_info[2])
	#master_data.insert(1,area_1_data)
	#master_tags.insert(1,area_1_tags)

    common_header = append_common_header(areas_found,area_length)
    common_header_tags = gen_common_header_tags()

    tag_bytes = append_sections(master_tags,common_header_tags)
    data_bytes = append_sections(master_data,common_header)


    if len(data_bytes)>memory_size:
       	print "Converted data size exceeds size of EEPROM"
        error_count=error_count+1
    print "\nSize of EEPROM according to XML file is : %d bytes"%memory_size
    print "Size of converted data : %d bytes"%len(data_bytes)




    if error_count==0:
        write_to_file(file_name,data_bytes,generate_addresses(len(data_bytes)),tag_bytes,debug)
    else:
        print "File not written due to error(s) shown"

########################################################################################################################
# MAIN FUNCTION CALL
########################################################################################################################

if __name__ == "__main__":


    ########################################
    # Options and help functions
    ########################################
    parser = optparse.OptionParser()
    parser.add_option("-r", "--run_script", dest="run", action="store_true",
        help =("Run the script and generate formatted output file"))
    #arser.add_option("-h", "--help",  help =("Help Options for GEN_FMC_EEPROM"))
    parser.usage = "\n\nusage:	python %prog [options] calibration_data_filename.txt \n\n Help Options for fmc_eeprom.py"
    parser.add_option("-i", "--file_in", dest="file_in", type="str",
        help =("Filename for output file [default:eeprom_formatted_data.txt]"))
    parser.add_option("-o", "--file_out", dest="file_out", type="str",
        help =("Filename for output file [default:eeprom_data.xml]"))
    parser.add_option("-t", "--types", action="store_true", dest="types",
      help =("Prints the valid types for fields in eeprom_data.xml"))
    parser.add_option("-m", "--multirecords", action="store_true", dest="multirecord",
      help =("Prints the valid options for MultiRecord types"))
    parser.add_option("-a", "--areas", action="store_true", dest="areas",
      help =("Prints the available Areas and their associated numbers"))
    parser.add_option("-c", "--calib", action="store_true", dest="calib_info",
      help =("Prints the required format for calibration data"))

    parser.add_option("-d", "--debug", action="store_true", dest="debug",
      help =("Add this option with -r to produce labels on output data"))

    opts, args = parser.parse_args()

    ########################################
    # Options process
    ########################################

    if opts.run:
    	main(opts.file_out,opts.file_in,opts.debug,args)
    if opts.multirecord:
        print_multi_record_options()
    if opts.types:
    	print_type_options()
    if opts.areas:
    	print_area_nums()
    if opts.calib_info:
    	print_calib_info()




