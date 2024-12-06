import requests

class GitLabUser:
    def __init__(self,url = None,token = None):
        self.url = 'https://git.datagrand.com/api/v4/'
        self.token = 'GD1qRfWy4kaDZCwYgY3z'
        self.users_url = self.url + f'users'
        self.tow_factor = {
            'enabled': True
        }
        self.headers = {
            'Private-Token': self.token
        }
    
    def addUser(self,name,username,email):
        user_data = {
                'name' : name,
                'username': username,
                'email': email,
                'password': '',
                'reset_password': True,
                'force_random_password': True
        }

        self.uid = None
        response = requests.post(self.users_url, headers=self.headers, json=user_data)
        if response.status_code == 201:
            user = response.json()
            user_id = user.get('id',None)
            print(user_id)
            if user_id != None:
                print('User created successfully')
                # self.twoFactor(user_id)
        else:
            print(f"Failed to create user. Status code: {response.status_code}, Error: {response.text}")
        self.uid = user_id
        return self.uid
        
    def twoFactor(self,uid):
        two_factor_settings_url  = self.url + f'users/{uid}/two_factor_settings'
 
        response = requests.put(two_factor_settings_url, headers=self.headers,json=self.tow_factor)

        if response.status_code == 200:
            print('Two-factor authentication enabled for the user')
        else:
            print(f"Failed to enable two-factor authentication. Status code: {response.status_code}, Error: {response.text}")


    # def activeOpt(self):
    #     optUrl = self.url + f'users/{self.uid}/otp'
    #     response = requests.post(optUrl, headers=self.headers)
    #     if response.status_code == 201:
    #         print('Two-factor authentication enabled and activation email sent')
    #     else:
    #         print(f"Failed to enable two-factor authentication. Status code: {response.status_code}, Error: {response.text}")

    def addProject(self,group_id = 54):
        group_url = self.url  + f'groups/{group_id}/members'
        member_data = {
            'user_id': self.uid,
            'access_level': 30  
        }
        response = requests.post(group_url, headers=self.headers, json=member_data)
        if response.status_code == 201:
            print('User added to group successfully')
        else:
            print(f"Failed to add user to group. Status code: {response.status_code}, Error: {response.text}")


#if __name__ == '__main__':
#    git = GitLabUser()
#    gitid = git.addUser('stonetest','stonetest','382331111@qq.com')
#    git.addProject()
    
