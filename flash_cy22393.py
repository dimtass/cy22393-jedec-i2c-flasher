#!/usr/bin/python
import re,sys,argparse,os

class CY22393:
    """
    Reads a CY22393 jedec file that is created using the cypress
    CyberClocks tool and then flashes the CY22393 chip using
    the specified I2C bus and address and/or writes the register
    values in two files (cy22393_reg08.txt and cy22393_reg40.txt).

    You can copy the content of the files inside the u-boot
    common/cmd_hd271_clocks.c in the appropriate byte arrays
    static const uint8_t clock_values_0x08[][16] and
    static const uint8_t clock_values_0x40[][24]

    author: Dimitris Tassopoulos
    """
    def __init__(self, filename):
        if not os.path.isfile(filename):
            raise FileNotFoundError
        self.m_fname = filename
        self.reg_values = self.readData(filename)
        #print(self.reg_values)

    def readData(self, fname):
        file = open(fname, "r")
        content = file.read()
        content = content.replace('\r', '')
        content = content.replace('\n','')
        # Get the bit values between the 'L00064' and '*'
        index1 = content.find("L00064", 0) + 6
        index2 = content.find("*", index1)
        bits = content[index1:index2]

        # Convert bits to bytes
        values = [[hex(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]]

        # Get the bit values between the 'L00512' and '*'
        index1 = content.find("L00512", 0) + 6
        index2 = content.find("*", index1)
        bits = content[index1:index2]

        # Convert bits to bytes
        values += [[hex(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]]
        file.close()
        return values

    def exportHeader(self):
        file = open("cy22393_reg08.txt", "w")
        file.write("{\n");
        for i in range(0x08, 0x17+1):
            file.write(self.reg_values[0][i-0x08] + ",")
        file.write("\n}");
        file.close()
        file = open("cy22393_reg40.txt", "w")
        file.write("{\n");
        for i in range(0x40, 0x57+1):
            file.write(self.reg_values[1][i-0x40] + ",")
        file.write("\n}");
        file.close()

    def writeValues(self, i2c_bus, i2c_addr):
        print("Start writing values starting from reg 0x08")
        for i in range(0x08, 0x17+1):
            print("\t{" + i2c_addr + "}: [" + hex(int(i)) + "] <- " + self.reg_values[0][i-0x08])
            os.system("i2cset -y " + i2c_bus + " " + i2c_addr + " " + hex(int(i)) + " " + self.reg_values[0][i-0x08])

        # Write values to registers 0x40 to 0x57
        print("Start writing values starting from reg 0x40")
        for i in range(0x40, 0x57+1):
            print("\t{" + i2c_addr + "}: [" + hex(int(i)) + "] <- " + self.reg_values[1][i-0x40])
            os.system("i2cset -y " + i2c_bus + " " + i2c_addr + " " + hex(int(i)) + " " + self.reg_values[1][i-0x40])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a CSV file with EXIF stats in a given path')
    parser.add_argument('-f', '--filename',
                        help='The jedec filename')
    parser.add_argument('-b', '--bus',
                        help='The I2C bus number to be used')
    parser.add_argument('-a', '--address',
                        help='The cy29323 I2C address (default is 0x69).')
    parser.add_argument('-e', '--export', action='store_true',
                        help='Export the values to a header file.')

    args = parser.parse_args()

    if args.filename == None:
        print("The jedec filename is needed.")
        parser.print_help()
        sys.exit(-1)

    cy = CY22393(args.filename)

    if (args.bus == None or args.address == None) and args.export == False:
        parser.print_help()
        sys.exit(-1)
    else:
        print("Using I2C bus: " + args.bus + " and address: " + args.address)
        cy.writeValues(args.bus, args.address)

    if args.export == True:
        print("Exporting reg values...")
        cy.exportHeader()
    
