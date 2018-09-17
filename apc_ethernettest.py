#!/usr/bin/python
# -*- coding:utf-8 -*-
import pdb

import re
import os
import sys
#import yaml
import time
import getpass
import pexpect
import logging
import commands
import subprocess
import ConfigParser
from argparse import ArgumentParser

def telnet_conn(ip_addr, port = 23):
    account = "apc"
    passwd = "apc"
    try:
        telnet_conn = pexpect.spawn("telnet %s %s" %( ip_addr, port))
        #telnet_conn.expect("Trying %s" % ip_addr)
        #telnet_conn.expect("Connected to %s" % ip_addr)
        #telnet_conn.expect("Escape character is '^]'")
        telnet_conn.expect("User Name :")
        telnet_conn.sendline(account)
        telnet_conn.expect("Password  :")
        print telnet_conn.before
        
        telnet_conn.sendline(passwd)
        telnet_conn.expect("Control Console")
        print telnet_conn.before

        ###### Enter top level : Device Manager######
        telnet_conn.expect("1- Device Manager")
        telnet_conn.sendline("1")
        telnet_conn.expect("Device Manager")
        print telnet_conn.before

        ###### Enter 2 level : Outlet Management#####
        telnet_conn.expect("2- Outlet Management")
        telnet_conn.sendline("2")
        telnet_conn.expect("Outlet Management")
        print telnet_conn.before

        ###### Enter 3 level : Outlet Control/Configuration#####
        telnet_conn.expect("1- Outlet Control/Configuration")
        telnet_conn.sendline("1")
        telnet_conn.expect("Outlet Control/Configuration")
        telnet_conn.expect("9- Master Control/Configuration")
        print telnet_conn.before

        print "telent connection sucess"
    except Exception:
        print "telent connection failed"
        return ''
    #### some operations #####
    return telnet_conn

def outlet_ctrl( telnet_conn, outlet_num, delay, state):
    '''
    telnet_conn : telnet control 
    outlet_num : 1 ~ 8
    state : 0 means off
            1 means on
            2 reboot
    '''
    try:
        print telnet_conn.before
        #pdb.set_trace()

        ##### outlet x has been chosen ######
        # why not matched ? not in one function is cleared
        #telnet_conn.expect("%s- Outlet %s                 ON" % (outlet_num, outlet_num))
        #telnet_conn.sendline("%s" % outlet_num)
        telnet_conn.send("%s\r" % outlet_num)
        telnet_conn.expect("Outlet %s" % outlet_num)
        print telnet_conn.before

        if delay != 0 :
            ###### Enter 5 level : Configure Outlet#####
            #pdb.set_trace()
            telnet_conn.expect("2- Configure Outlet")
            telnet_conn.sendline("2")
            telnet_conn.expect("Configure Outlet")
            print telnet_conn.before
            ###### state == 0 : Outlet x off#####
            if state == 0 :
               #pdb.set_trace()
               telnet_conn.expect("3- Power Off Delay")
               telnet_conn.sendline("3")
               telnet_conn.expect("Power Off Delay Range: -1 to 7200 sec, where -1=Never")
               print telnet_conn.before
            ###### state == 1 : Outlet x on#####
            elif state == 1 :
               telnet_conn.sendline("2")
               telnet_conn.expect("Power On Delay")
               print telnet_conn.before
            else :
                print "No State Chosen, Please Check State Val"

            telnet_conn.sendline("%s" % delay)
            telnet_conn.expect("Accept Changes      : Pending")
            print telnet_conn.before

            telnet_conn.sendline("5")
            telnet_conn.expect("Accept Changes      : Success")
            print telnet_conn.before
            
            ##### send ESC back to outlet x dashboard ######

        else :
        #### some operations directly #####
            telnet_conn.expect("1- Control Outlet")
            telnet_conn.sendline("1")
            telnet_conn.expect("Control Outlet")
            if state == 0 :
               telnet_conn.expect("5- Delayed Off") 
               telnet_conn.sendline("5")
            elif state == 1 :
               telnet_conn.expect("4- Delayed On") 
               telnet_conn.sendline("4")
            else :
               print "No State Chosen, Please Check State Val"

            #pdb.set_trace()
            telnet_conn.expect("Enter 'YES' to continue or <ENTER> to cancel")
            telnet_conn.sendline("YES")
            telnet_conn.expect("Command successfully issued")
            telnet_conn.expect("Press <ENTER> to continue...")
            telnet_conn.sendline("\r")
            telnet_conn.expect("Control Outlet")


        ##### send ESC back to outlet x dashboard ######
        #### Operations Over, Recovery Environment #####
        telnet_conn.sendline("\x1b")    
        telnet_conn.expect("2- Configure Outlet")
        telnet_conn.sendline("\x1b")    
        telnet_conn.expect("Outlet Control/Configuration")


        print telnet_conn.before
    except Exception:
        print "outlet ctrl failed"
        return False
    #### some operations #####
    return True

def initial_sysstatus(telnet , switch_delay):
    ###### Initialize Outlet 1-5 :Server Status, Delay 5 , ON  ######
    try:
        for i in range(1, 3):
            outlet_ctrl( telnet, i, 70, 1)	
            outlet_ctrl( telnet, i, 0, 1)



        outlet_ctrl( telnet, 6, switch_delay, 1)	
        outlet_ctrl( telnet, 6, 0, 1)
	
#        ###### Initialize Outlet 6 :Switch Status, Delay 5 , OFF  ######
#        outlet_ctrl( telnet, 6, 5, 0)	
#        outlet_ctrl( telnet, 6, 0, 0)
#        time.sleep(5)
#        ###### Outlet 6 :Switch , Configure 180sec, to set up #####
#        outlet_ctrl( telnet, 6, 180, 1)
#        outlet_ctrl( telnet, 6, 0, 1)

#        ###### Initialize Outlet 6 :Switch Status, Delay 5 , OFF  ######
#        outlet_ctrl( telnet, 6, 5, 1)	
#        outlet_ctrl( telnet, 6, 0, 1)
#        time.sleep(5)

        print "Initial System Status Sucess"
    except Exception:  

        print "Initial System Status failed"
        return False

    return True

def shutdown_sys(telnet ):
    ###### Shutdown Outlet 1-5 :Server Status & Switch, Delay 5 , OFF  ######
    try:
        for i in range(1, 3):
            outlet_ctrl( telnet, i, 5, 0)
            outlet_ctrl( telnet, i, 0, 0)


        outlet_ctrl( telnet, 6, 5, 0)
        outlet_ctrl( telnet, 6, 0, 0)

#    try:
#        for i in range(1, 6):
#            outlet_ctrl( telnet, i, 5, 0)
#            outlet_ctrl( telnet, i, 0, 0)


        print "Shutdown System Sucess"
    except Exception:
        print "Shutdown System Sucess"
        return False 

    return True

def network_statusjudge(ip_list, netlog):
    for ip in ip_list :
        #print IP
        print "ssh -v root@%s" % ip
        ssh_conn = pexpect.spawn("ssh -v root@%s" % ip)
        
        try:
            ssh_conn.expect("Connection established")
            print ("%s: Ssh Connection OK" % ip)

            ssh_conn.sendline("busybox devmem 0xc7000170")
            value1 = ssh_conn.expect("0x00000000")
          
            #ssh_conn.sendline("busybox devmem 0xc7002210")
            #value2 = ssh_conn.expect("0x00000100")

            ssh_conn.sendline("busybox devmem 0xc7001234")
            value3 = ssh_conn.expect("0x00000000")
            #if value1 != 0 or value2 != 0 or value3 != 0 :
            if value1 != 0 or value3 != 0 :
                print ("%s: regread symbol error" % ip)             
                netlog.info("\n%s:  regread symbol error\n" % ip)    
                return 0                                             
            ssh_conn.sendline("exit")
            ssh_conn.expect("Connection to %s closed" % ip)
            netlog.info("\n %s: Ssh Connection OK \n" % ip)
        except Exception:                                        
            print ("%s: Ssh Connection Failed" % ip)             
            netlog.info("\n%s: Ssh Connection Failed\n" % ip)    
            return 0                                             
                                                                 
    return 1                                                     
    
    
    
def network_sshconn(ip_list, netlog):
    for ip in ip_list :
        #print IP
        print "ssh -v root@%s" % ip
        ssh_conn = pexpect.spawn("ssh -v root@%s" % ip)
        
        try:
            ssh_conn.expect("Connection established")
            print ("%s: Ssh Connection OK" % ip)
            ssh_conn.sendline("exit")
            ssh_conn.expect("Connection to %s closed" % ip)
            netlog.info("\n %s: Ssh Connection OK \n" % ip)
        except Exception:
            print ("%s: Ssh Connection Failed" % ip)
            netlog.info("\n%s: Ssh Connection Failed\n" % ip)
            return 0

    return 1

def network_pingdelay(ip_list, netlog):
    for ip in ip_list :
        #print IP
        print "test ip is %s" % ip
        status,output = commands.getstatusoutput("ping -c 26 '%s'" % ip)
        #pdb.set_trace()
        if status != 0:
           print ("%s: Ping Failed" % ip)
           netlog.info("\n"+output+"\n")
        else:
          if re.findall("time=([0-9]+.[0-9]+)", output):
             delay = re.findall("time=([0-9]+.[0-9]+)", output)

          for tvalue in delay :
                if float(tvalue) > 1000 :
                    print ("%s: Ping Success" % ip)
                    netlog.info("\n"+output+"\n")
                    return 0
                else:
                    print ("%s: Ping Unsatisfied, Reboot " % ip)
                    netlog.info("\n"+output+"\n")
    return 1

if __name__ == "__main__":

    logging_format = '%(asctime)s %(levelname)-5.5s| %(message)s'    
    date_format = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(filename='pingtest.log',level=logging.DEBUG, format=logging_format, datefmt=date_format )
    result_log = logging.getLogger()
    
    #ip_list = ["192.168.1.79", "192.168.1.48", "192.168.1.146", "192.168.1.130", "192.168.1.181" ] 
    ip_list = ["192.168.1.79", "192.168.1.48"] 

    ip_addr = "192.168.2.203"
    telnet = telnet_conn( ip_addr)
    ##### Initialize First ,Make System Status normal #######    
    switch_delay = 75
    test_num = 1
    initial_sysstatus(telnet, switch_delay )
    #print "wait 420s == 7min , to make system get up competely ..."
    print "wait 600s == 10min , to make system get up competely ..."
    time.sleep(600)
    #pdb.set_trace()
    while(True) :
      if (switch_delay > 240) :
         switch_delay = 5
      print "\n============Current Switch Delay is %d sec=\n" % switch_delay
      print "\n============Current No.%s Test=============\n" % test_num
      result_log.info("\n============Current Switch Delay is %d sec=\n" % switch_delay)
      result_log.info("\n============Current No.%s Test============ \n" % test_num)
      #pdb.set_trace()
      #result = network_delay(ip_list ,result_log)
      #result = network_sshconn(ip_list ,result_log)
      result = network_statusjudge(ip_list ,result_log)
      #######Inactivity timeout exceeded. Initial telnet Again############
      telnet = telnet_conn( ip_addr)
      
      print " system test result is %s " % result    
      if result == 1 :
         #pdb.set_trace()
         shutdown_sys( telnet)
      else :
         print "System network question has been recurring" 
         break
      #pdb.set_trace()
      initial_sysstatus(telnet, switch_delay)
      #switch_delay = switch_delay + 1 
      switch_delay = switch_delay + 10 
      test_num = test_num + 1
      time.sleep(600)























