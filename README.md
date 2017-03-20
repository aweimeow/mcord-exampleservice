## 

## How to build this service

```bash
ssh prod         # ssh into vagrant
git clone https://github.com/aweimeow/mcord_homework ~/xos_services/exampleservice
```

and add following configuration into your your `~/service-profile/mcord/MakeFile`


```MakeFile
    onboarding:

        ...

        sudo cp id_rsa key_import/exampleservice_rsa
        sudo cp id_rsa.pub key_import/exampleservice_rsa.pub

        ...

        bash $(COMMON_DIR)/wait_for_onboarding_ready.sh $(XOS_BOOTSTRAP_PORT) services/exampleservice

        ...
```
