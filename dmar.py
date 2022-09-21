import sys
import os
import queue
import subprocess
import argparse
from collections import defaultdict
from colorlog import ColoredFormatter
import logging


def setup_logging():

    file_handler = logging.FileHandler(filename='./_ps{0}.log'.format(os.getpid()))
    stdout_handler = logging.StreamHandler(sys.stdout)
    LOGFORMAT = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
    LOGFORMAT2 = "[%(asctime)s] - %(message)s"
    formatter = ColoredFormatter(LOGFORMAT)
    stdout_handler.setFormatter(formatter)
    handlers = [file_handler, stdout_handler]

    logging.basicConfig(
        level=logging.DEBUG,
        #format='[%(asctime)s] - %(message)s',
        handlers=handlers
    )

if __name__ == "__main__":
	
    setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num", help="Enter the number of VTd units BIOS is expected to enumerate")
    args = parser.parse_args()

    if(args.num!=None):
        #Store Expected Num of Vtd Units
        expected_num=int(args.num)
        logging.info("| The BIOS reports the remapping hardware units in a platform to system software through the DMAR ACPI table")
        logging.info("| BIOS is expected to enumerate " + args.num + " instances of IOMMU for this platform")
        logging.info("| Installing Required Packages for ACPI Dump")
        try:
            ret = os.system('apt install acpidump')
            if(ret!=0):
                logging.error("| ERROR : Couldn't install ACPI Dump packages :(")


        except:
            logging.error("| ERROR : Couldn't install ACPI Dump packages :(")


        else:
            logging.info("| ACPI Dump Successfully Installed ")
            path = os.path.join(str(os.getcwd()), ("dmar_log_"+str(os.getpid())))
            print(path)
            os.mkdir(path)
            os.chdir(path)
            logging.info("| Dumping all acpi tables in binary format ")
            try:
                ret = os.system('acpidump -b')
                if(ret!=0):
                    logging.error("| ERROR : Couldn't dump the acpi tables :(")

            except:
                logging.error("| ERROR : Couldn't dump the acpi tables :(")

            else:
                logging.info("| ACPI Tables dumped SUCCESSFULLY in binary format ")
                logging.info("| Converting DMAR binary file to readable format")
                ret = os.system('iasl dmar.dat')
                count = open('dmar.dsl', 'r').read().count("Hardware Unit Definition")
                logging.info("| Number of occurances of IOMMU in ACPI Dump = " + str(count))
                print(type(count))
                if(count != int(args.num)):
                    logging.error("| FAILED. Expected Number of IOMMUs is = " + str(args.num) + " .But DMAR has " + str(count))
                else:
                    logging.info("| Number of occurances of IOMMU in ACPI Dump = " + str(count))
                    
                logging.info("| Checking Number of VTd units in /sv ")
                try:
                    ret = os.system('ls /sv | grep vtd')
                    if(ret!=0):
                        logging.error("| ERROR : No vtd detected under /sv. Is VTd enabled in BIOS? ")

                except:
                    logging.error("| ERROR : No vtd detected under /sv. Is VTd enabled? ")

                else:
                    logging.info("| Found VTd Node in /sv")
                    logging.info("| Checking Number of VTd Units under /sv/vtd")
                    out = subprocess.Popen("ll /sv/vtd | grep -c vtdunit-non", stdout=subprocess.PIPE)
                    vtd_nodes = p.communicate()[0]
                    if(vtd_nodes != int(args.num)):
                        logging.error("| FAILED. Expected Number of VTd Units in SVOS is = " + str(args.num) + " .But /sv has " + str(vtd_nodes) + "Nodes")
                    else :
                        logging.info("| Found" + str(vtd_nodes) + "VTd Nodes in /sv")

    else:
        logging.info("| No Arguments passed. Pass the VTd units BIOS is expected to enumerate like --num 4")



