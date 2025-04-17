# availability-check
ansible roles for services availability check

## HTCondor 시스템에서의 Availability Check 세팅방법 (예제는 serviceB 기준)
### 패키지 다운로드
1. admin-console에서 시작해야합니다.
2. 아래 명령어로 git clone을 합니다.
   ```bash
   git clone https://github.com/gsdc/availability-check.git
   ```
   * (안내) 저장소에 접근할 때 github 계정과 token을 입력 받습니다.
3. 새로운 브랜치를 만들어서 이를 이용하도록 합니다.
   ```bash
   git checkout -b serviceB
   ```
### Role 파일 수정
1. 받아진 git 저장소의 ```roles/availability-check/tasks```디렉토리에서 ```serviceA``` 디렉토리를 본인의 서비스 이름으로 복사합니다.
   ```bash
   roles/availability-check/tasks
   cp -r serviceA serviceB   
   ```
###  group_vars 수정
1. git 저장소 최상위 디렉토리에 있는 ```group_vars/``` 로 이동하여 서비스 관련 디렉토리를 만들고 ```group_vars/serviceA/vars.yml```을 복사합니다.
   ```bash
   cd -
   cd group_vars/
   mkdir serviceB/
   cp serviceA/vars.yml serviceB/
2. 서비스 디렉토리로 이동하여 암호화된 변수 파일을 생성합니다.
   ```bash
   cd serviceB/
   ansible-vault create vault_vars.yml
   ```
   * [안내] 생성 혹은 수정하려면 ansible vault 암호 입력이 필요하며, 혹시 수정이 필요하다면 ```ansible-vault edit vault_vars.yml``` 로 수정이 가능합니다.
3. 아래 내용을 기반으로 내용을 수정합니다. (따옴표 포함)
   ```bash
   ansible_ssh_pass: "[접속 암호]"
   ansible_became_pass: "{{ ansible_ssh_pass }}"
   voms_pw: "[voms-proxy-init 암호]"
   ```
4. ```group_vars/[service]/vars.yml```을 적절하게 수정합니다.
   * ```checkmode```는 가용성을 테스트할 때 사용되는 결정 정책입니다.
      * **optimistic** (default) : ```group_vars/all/vars.yml```. 다중 서버가 타켓일때, 각 서버의 체크리스트는 ```AND```, 서버별로는 ```OR``` 되어 최종 가용성을 결정.
      * **pessimistic** : overridable in ```group_vars/[service]/vars.yml```. 다중 서버가 타켓일때, 각 서버의 체크리스트는 ```AND```, 서버별로도 ```AND``` 되어 최종 가용성을 결정.     
   * ```checklist```는 테스트할 metric입니다.
      * **connectivity**: 해당 서비스의 테스트를 진행할 UI 혹은 테스트 서버와의 접속이 가능한지와 ssh 데몬이 제대로 동작 중인지를 점검합니다.
      * **storageio**: 해당 서비스 테스트 서버에서 점검할 (마운트된) 디렉토리의 상태를 확인합니다. 관련 변수들은 아래와 같습니다.
         * ```nfs_mountpoint```: 마운트된 경로입니다. NFS일 필요는 없으나 디렉토리 마운트 여부를 확인하므로 로컬 디스크 등은 오류가 발생합니다.
         * ```nfs_write_test_path```: 해당 경로에서 쓰기 작업 테스트를 진행할 경로입니다. 해당 경로는 접속할 계정으로 쓰기 작업이 가능해야 합니다.
      * **xrootd**: XRootD 프로토콜 테스트를 진행합니다. 관련 변수들은 아래와 같습니다.
         * ```xrootd_hostname```: XRootD Redirector 서버 이름입니다.
         * ```xrootd_port```: XrootD redirector 데몬의 포트 번호입니다. 생략할 경우, 기본값은 1094입니다.
         * ```xrootd_check_files```: xrootd 경로상의 테스트할 파일들의 목록입니다. 모든 파일들을 체크하며 하나라도 실패하면 오류가 발생합니다.
         * ```command_timeout```: ```xrootd_check_files```를 점검할 때의 timeout 시간입니다. 해당 시간이 지나면 테스트가 종료되며 실패로 처리합니다.
         * ```xrootd_write_test_path```: xrootd 경로상에서 쓰기 작업이 가능한 디렉토리 경로입니다.         
      * **webdav**: WebDAV 프로토콜 테스트를 진행합니다. 관련 변수들은 **xrootd** 와 프로토콜 이름만 다르고 동일합니다.
         * ```webdav_port```: 기본 포트는 2880입니다. 다를 경우에만 설정하면 됩니다.
      * **batch**: HTCondor 데몬들의 상태를 확인합니다.
      * **job**: HTCondor 테스트 작업을 제출합니다. 제출 후, 특정시간동안 작업 종료를 기다립니다. 관련 변수들은 아래와 같습니다.
         * ```accounting_group```: HTCondor Accounting Group 설정이 있을 경우, 해당 accoungting_group을 설정합니다.
         * ```condor_job_timeout```: 작업 제출 후, 해당 작업 종료까지의 대기시간을 지정합니다. 해당 시간이 지나도록 작업이 종료되지 않으면 강제로 작업이 취소되며 테스트는 실패가 됩니다.
   * ```ansible_user```: 테스트 서버에 접속할 계정입니다.
### 테스트 셋업
1. ```hosts``` 파일에 서비스 관련 정보가 올바르게 적혀있는지 확인합니다.
   * [서비스] 및 [테스트 서버] 정보
     ```
     [serviceB]
     serviceB-ce2.sdfarm.kr ansible_host=192.168.10.100
     ```
1. git  저장소 최상위 디렉토리에서 ```serviceA.yml```을 ```[서비스].yml```로 복사합니다.
   ```bash
   cd -
   cp serviceA.yml serviceB.yml
   ```
1. ```[서비스].yml``` 파일을 적절하게 수정합니다.
   ```bash
   hosts: serviceA => hosts: serviceB
   ```
1. ansible vault 패스워드 파일을 생성합니다.
   ```bash
   echo "[Ansible Valut Password]" > .vault_pass
   ```
1. ```ANSIBLE_VAULT_PASSWORD_FILE``` 환경변수로 ansible vault 패스워드 파일을 지정합니다.
   ```bash
   export ANSIBLE_VAULT_PASSWORD_FILE=./.vault_pass
   ```
1. 테스트를 실행합니다.
   ```bash
   ansible-playbook serviceB.yml
   ```
### 테스트가 성공적으로 이루어지면 Github에 올립니다.
1. git status 로 확인한 수정 파일들을 git add 한 후에 commit 합니다.
   ```bash
   git status
   git add group_vars/serviceB/vars.yml group_vars/serviceB/vault_vars.yml roles/availability-check/tasks/~~~
   git commit -m "ServiceB용 테스트 코드 작성"
   git push origin serviceB # git push origin [branch]
   ```
   * .vault_pass 같은 비밀번호 파일이나 임시 파일들은 제외해야 합니다.
### WorkNode 설정
1. WN들 중 하나를 임의로 선정하여 아래 옵션을 추가로 지정합니다. 아래 설정은 ```/etc/condor/config.d/cluster.conf``` 보다 항상 뒤에 실행되도록 이름을 지정해야 합니다.
   ```bash
   echo "~~~" > /etc/condor/config.d/test_condor.conf
   ```
   * (안내) 내용 중 testuser만 접속 계정명으로 변경하시면 됩니다.
```bash
NUM_CPUS = $(DETECTED_CORES)+1
NUM_SLOTS = 2

NUM_SLOTS_TYPE_2 = 1
SLOT_TYPE_2 = cpus=1, ram=4096,disk=5%
SLOT_TYPE_2_PARTITIONABLE = True
NUM_SLOTS_TYPE_1 = 1
SLOT_TYPE_1 = cpus=$(DETECTED_CORES), ram=auto, disk=auto
SLOT_TYPE_1_PARTITIONABLE = True
START=(SlotID==1)||((SlotID==2)&&(Owner=="testuser"))
```
