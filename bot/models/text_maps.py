
choice_message_map = {
    'find_contact': "Найти контакты сотрудника",
    'gain_access': "Получить доступ",
    'order_cutaway': "Заказать визитку",
    'order_office': "Заказать канцелярию",
    'order_pass': "Заказать пропуск",
    'order_technic': "Заказать/отремонтировать технику"
    

}

get_info_message_map = {
    'find_contact': "Введите ФИО сотрудника контакты которого вам нужны:",
    'gain_access': "Введите информацию о доступе который вам необходимо предоставить:",
    'order_cutaway': "Введите ФИО сотрудника для которого вам нужна визитка:",
    'order_office':"Введите товары которые нужно заказать:",
    'order_pass': "Введите ФИО человека для которого нужно заказать пропуск:",
    'order_technic': "Опишите свою проблему:"
} 

success_message_map = {
    'find_contact': "поиск контактов сотрудника",
    'gain_access': "предоставление доступа",
    'order_cutaway': "создание визитки",
    'order_office': "заказ канцелярии",
    'order_pass': "заказ пропуска",
    'order_technic': "вызов технического специалиста"
} 

order_map = {
            'find_contact': {
                'type_order': 'запрос контакта!',
                'order_info': 'Имя контакта'
            },
            'gain_access': {
                'type_order': 'запрос доступа!', 
                'order_info': 'Тип доступа'
            },  
            'order_cutaway': {
                'type_order': 'запрос визитки!',
                'order_info': 'На чье имя визитка'
            },
            'order_office': {
                'type_order': 'заказ канцелярии!', 
                'order_info': 'Требуемые товары',
            },  
            'order_pass': {
                'type_order': 'заказ пропуска!', 
                'order_info': 'На чье имя пропуск'
            },
            'order_technic': {
                'type_order': 'вызов специалиста!', 
                'order_info': 'Тип поломки'
            }
        }