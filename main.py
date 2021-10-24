import sys
import vk_api
import pandas as pd
import networkx as nx

class EdgeList:

    def __init__(self, id, vkApi):
        self.friends = set(vkApi.friends.get(user_id = id)['items'])
        self.id = id

        self.list_of_friends = []
        self.friends_of_friends = set()
        for friend_id in self.friends:
            status = 'exists'
            if vkApi.users.get(user_id = friend_id)[0].get('deactivated') != None:
                status = vkApi.users.get(user_id = friend_id)[0]['deactivated']
            if status != "banned" and status != "deleted" and vkApi.users.get(user_id = friend_id)[0]['is_closed'] == False:
                self.list_of_friends = self.list_of_friends + list(vkApi.friends.get(user_id = friend_id)['items'])

        self.friends_of_friends = set(self.list_of_friends)

        if id in self.friends_of_friends:
            self.friends_of_friends.remove(id)

        static_friends_of_friends = list(self.list_of_friends)

        for current_user in static_friends_of_friends:
            status = 'exists'
            if vkApi.users.get(user_id=current_user)[0].get('deactivated') != None:
                status = vkApi.users.get(user_id=current_user)[0]['deactivated']
            if status == "banned" or status == "deleted" or vkApi.users.get(user_id=current_user)[0]['is_closed'] == True and current_user in self.friends_of_friends:
                self.friends_of_friends.remove(current_user)

    def get_info_csv(self):

        is_friend = []
        is_friend_of_friend = []
        friend_id = []
        friend_link = []
        friend_name = []
        friend_surname = []

        friends_union = self.friends | self.friends_of_friends

        for friend in friends_union:
            is_friend.append(friend in self.friends)
            is_friend_of_friend.append(friend in self.friends_of_friends)
            friend_id.append(friend)
            friend_name.append(vkApi.users.get(user_id = friend)[0]['first_name'])
            friend_surname.append(vkApi.users.get(user_id=friend)[0]['last_name'])

        data = {"id пользователя": friend_id, "Является ли другом": is_friend, "Является ли другом друга": is_friend_of_friend, "Имя": friend_name, "Фамилия": friend_surname}

        result_dataframe = pd.DataFrame(data)
        result_dataframe.to_csv('data.csv', sep=' ', index = False)

    def get_info_gephi(self):

        result_graph = nx.Graph()

        for current_friend in self.friends:
            result_graph.add_edge(self.id, current_friend)
            status = 'exists'
            if vkApi.users.get(user_id = current_friend)[0].get('deactivated') != None:
                status = vkApi.users.get(user_id = current_friend)[0]['deactivated']
            if status != "banned" and status != "deleted" and vkApi.users.get(user_id = current_friend)[0]['is_closed'] == False:
                for current_friend_of_friend in vkApi.friends.get(user_id = current_friend)['items']:
                    if current_friend_of_friend in self.friends_of_friends:
                        result_graph.add_edge(current_friend, current_friend_of_friend)

        nx.write_gexf(result_graph, "test.gexf")



def auth():
    print("Введите логин от своего профиля вконтакте:", end=' ')
    login = input()
    print("Введите пароль от своего профиля вконтакте:", end=' ')
    password = input()
    vk_session = vk_api.VkApi(login, password)
    vk_session.auth()

    vkApi = vk_session.get_api()

    return vkApi

vkApi = auth()

print("Добро пожаловать," + vkApi.users.get()[0]['first_name'] + "!")

print("Введите id пользователя, информацию о друзьях для которого вы хотите узнать:", end=' ')
id = input()

system = EdgeList(id, vkApi)

system.get_info_gephi()