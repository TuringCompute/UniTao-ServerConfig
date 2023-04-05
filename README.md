# UniTaoServer
Inventory(UniTAO) Data Driven Server Configuration Automation

### the challenge of Server Configuration Automation:
 - Data is embedded inside different server automation language it makes hard to migrate from one language to other
 - it's hard to understand what is the expected state the target server to be
 - since all configuration data is embedded in code, it makes everything hard coded.
 - all relationships between inventory resources are managed by inventory system instead of execution role(UniTaoServer).

As the name of this project suggested, we are trying to use UniTAO Inventory Data Schema to represent all component 
that needs to be created and configured in the server. so the data and logic can be separated. thus we can manipulate server
from current state to desired state. this is more like a Terraform instead of ansible way.

### For Example: To achieve the following in server:
1. ensure apache is at the latest version
2. Write the apache config file.

**With Ansible:** 
data and logic are mixed together as following
```yaml
- name: Update web servers
  hosts: webservers
  remote_user: root

  tasks:
  - name: Ensure apache is at the latest version
    ansible.builtin.yum:
      name: httpd
      state: latest
  - name: Write the apache config file
    ansible.builtin.template:
      src: /srv/httpd.j2
      dest: /etc/httpd.conf
```

**With Inventory:(TODO: We will add code block later)**
1. Collect Current State of Apache Server
2. Compare Current State with Desired State
3. decide change/action from there.


