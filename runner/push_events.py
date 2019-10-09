#!/usr/bin/python
import requests
import datetime
import socket
import psutil
import time

payload_value_dict = dict()
now = datetime.datetime.now()

def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;
 
def findProcessIdByName(processNames):
    '''
    Get a list of all the PIDs of a all the running process whose name contains
    the given string processName
    '''
 
    listOfProcessObjects = []
 
    #Iterate over the all the running process
    for proc in psutil.process_iter():
       try:
           pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
           # Check if process name contains the given name string.
           if pinfo['name'].lower() in processNames:
               pinfo.update({'duration_in_seconds': time.time() - pinfo['create_time']})
               listOfProcessObjects.append(pinfo)
       except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess) :
           pass
 
    return listOfProcessObjects;
 
#
job_name='custom_windows_build_metrics'
instance_name='{}'.format(socket.gethostname())
provider='stark_team'
payload_key='windows_build_tracker'
#payload_value='25.90'
payload_value=payload_value_dict
pushgateway_service='prometheus-pushgateway.monitoring.svc'
pushgateway_service_port='9091'

base_post_url = 'http://{pgs}:{pgsport}/metrics/job/{j}/team/{t}'.format(pgs=pushgateway_service, pgsport=pushgateway_service_port, j=job_name, t=provider)

def main(process_names_to_track=None):
    while True:
        processed_objects = findProcessIdByName(process_names_to_track)
        for processes in processed_objects:
            duration_in_secs = processes.get('duration_in_seconds', 0)
            response = requests.post('http://{pgs}:{pgsport}/metrics/job/{j}/instance/{i}/team/{t}/create_time/{c_time}/process_name/{name}/pid/{pid}'.format(pgs=pushgateway_service, pgsport=pushgateway_service_port, i=instance_name, j=job_name, c_time=time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(processes['create_time'])), name=processes['name'], t=provider, pid=processes['pid']), data='{k} {v}\n'.format(k=payload_key, v=duration_in_secs))
            #response = requests.post(combined_url, data='{k} {val}\n'.format(k=payload_key, val=duration_in_secs))
            print(response.status_code)
        time.sleep(60)

if __name__ == '__main__':
    process_names = ['make_win_pkgs.sh', 'gen_win_build_deps.sh', 'build_win_agents.sh', 'build_win_remote.sh', 'build_win_image_converter.sh']
    # Have to truncate process_names to 15 charachters
    # because psutil only spits out 15 character process names
    process_name_truncated = [ x[:15] for x in process_names ]
    print(process_name_truncated)
    main(process_name_truncated)
