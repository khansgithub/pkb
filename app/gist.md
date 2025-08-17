# git
### global user.email user.name
```bash
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```
#### switch user and choose which shell to use
```bash
su -s /bin/bash <user>
```
#### credential cache helper
```bash
git config --global credential.helper cache
git config --local credential.helper cache

git config --global --unset credential.helper
```
#### disable credential helper for single command
```bash
git clone https://bitbucket.org/<repo>.git --config credential.helper=
```