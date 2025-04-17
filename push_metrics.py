import argparse
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from prometheus_client.exposition import basic_auth_handler

def dict2availability(results, mode):
	availability = False 
	if mode == 'pessimistic':	 
		for r in results.values():
			availability = all(r.values())
			if not availability: 
				break
		print(availability)
		return availability
	elif mode == 'optimistic':
		tmp = []
		for r in results.values():
			tmp.append(all(r.values()))
		print(tmp, any(tmp))
		availability = any(tmp)
		return availability 
	else:
		return availability

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="push_metrics.py", description='''This program aims to push raw availability metrics of services to prometheus servers''', epilog='')
    parser.add_argument('-e', '--endpoint', required=True)
    parser.add_argument('-s', '--service', required=True)
    parser.add_argument('-m', '--mode', required=True)
    parser.add_argument('-l', '--checklist', required=True)
    parser.add_argument('-r', '--result', required=True)
    args = parser.parse_args()
    args_dict = vars(args)

    endpoint = args_dict['endpoint']
    serviceName = args_dict['service']
    mode = args_dict['mode']
    check_list = args_dict['checklist'].split(',')
    result_dict = eval(args_dict['result'])


    nodes = list(result_dict.keys())

    registry = CollectorRegistry()
    connectivity_g = Gauge('avail_connectivity', 'Connectivity Test', ['service', 'node'], registry=registry)
    storageio_g = Gauge('avail_storageio', 'StorageIO Test', ['service', 'node'], registry=registry)
    xrootd_g = Gauge('avail_xrootd', 'XRootD Test', ['service', 'node'], registry=registry)
    webdav_g = Gauge('avail_webdav', 'WebDav Test', ['service', 'node'], registry=registry)
    batch_g = Gauge('avail_batch', 'Batch System Test', ['service', 'node'], registry=registry)
    job_g = Gauge('avail_job', 'Pilot Job Test', ['service', 'node'], registry=registry)
    availability_g = Gauge('avail_availability', 'Service Availability', ['service'], registry=registry)

    availability_g.labels(service=serviceName).set(int(dict2availability(result_dict, mode)))
    for check in check_list:
        if check == 'connectivity':
            for nodeName in nodes:
                connectivity_g.labels(service=serviceName, node=nodeName).set(int(result_dict[nodeName][check]))   
        elif check == 'storageio':
            for nodeName in nodes:
                storageio_g.labels(service=serviceName, node=nodeName).set(int(result_dict[nodeName][check]))
        elif check == 'xrootd':
            for nodeName in nodes:
                xrootd_g.labels(service=serviceName, node=nodeName).set(int(result_dict[nodeName][check]))
        elif check == 'webdav':
            for nodeName in nodes:
                webdav_g.labels(service=serviceName, node=nodeName).set(int(result_dict[nodeName][check]))     
        elif check == 'batch':
            for nodeName in nodes:
                batch_g.labels(service=serviceName, node=nodeName).set(int(result_dict[nodeName][check]))
        elif check == 'job':
            for nodeName in nodes:
                job_g.labels(service=serviceName, node=nodeName).set(int(result_dict[nodeName][check]))

    push_to_gateway(endpoint, job=serviceName, registry=registry)
