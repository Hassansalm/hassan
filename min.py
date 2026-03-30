import ssl
import os

# هذا السطر يخبر بايثون بتجاهل فحص شهادات SSL
ssl._create_default_https_context = ssl._create_unverified_context
from flet  import *

  #### main ######
def main(page:Page):
    page.title='hassan.salm program'
    page.window.width = 400
    page.window.height = 800
    page.window.top = 15 
    page.window.left = 950
    page.vertical_alignment = "center"
    page.horizontal_alignment =  "center"
    page.bgcolor = Colors.BLUE

  ###### end main ####

  ###### appbar start ####
    page.appbar = AppBar(
        bgcolor = Colors.BLUE ,
        title = Text("program" , color='black' ) ,
        center_title=True , 
        leading=Icon(Icons.HOME ) , 
        leading_width= 50 , 
        #### الاحداث او الايقونة ####
        actions=[
            IconButton(Icons.NOTIFICATIONS ,icon_color=Colors.AMBER) ,
            PopupMenuButton( 
                items=[
                    PopupMenuItem(Text('الملف الشخصي' , size=14 ,weight=FontWeight.BOLD) ) ,
                    PopupMenuItem(Text('اعدادات التطبيق' , size=14 ,weight=FontWeight.BOLD) ) ,
                    PopupMenuItem() ,
                    PopupMenuItem(Text('من نحن ' , size=14 ,weight=FontWeight.BOLD) ) ,
                    PopupMenuItem(Text('اغلاق التطبيق' , size=14 ,weight=FontWeight.BOLD) ) ,
                    
                  
                ]
                
            )

        ]

    )
    ######appbar end #######

    ##### التحقق####
    def show(e):
        v1 =en1.value 
        v2= en2.value


        if v1 == 'hassan' and v2 == 'MHMh5656' :
          
          alert1= AlertDialog(
             title=Text("welcom admin" ,size=20 , color='green')
         )
          
          page.overlay.append(alert1)
          alert1.open=True
          page.update()
        else:
           alert1 =AlertDialog(
              title= Text('data error' , size=25 , color='red')
           )
           page.overlay.append(alert1)
           alert1.open=True
           page.update()
             
  
    ###### tolsss ########
    img = Image(src=f'123.jpg', width=180, height=200)
    txt=Text("تسجيل الدخول " ,color='Black',size= 25)
    en1 = TextField(label='Email(اسم المستخدم)' , icon=Icons.EMAIL)
    en2 = TextField(label='password(كلمة المرور)' , icon=Icons.PASSWORD ,password=True , can_reveal_password=True)
    btn = ElevatedButton('login - تسجيل الدخول' ,on_click=show)


    page.add(img , 
             txt ,
             en1 , 
             en2 , 
             btn 
             )
    
    ##### navigation bar #### 
    page.navigation_bar = CupertinoNavigationBar(
       bgcolor=Colors.BLUE ,
       inactive_color= Colors.BLACK , 
       destinations=[
          NavigationBarDestination(icon=Icons.CALL,label='call') ,
          NavigationBarDestination(icon=Icons.CAMERA , label='camera') ,
          NavigationBarDestination(icon=Icons.CONTACT_EMERGENCY , label='contact')
       ]
    )
    page.update()

app(main)
