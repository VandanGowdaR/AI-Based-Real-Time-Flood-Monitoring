import matplotlib.pyplot as plt
x=['Bangalore','Chennai','Kochi','Mumbai']
y=[100,600,400,500]
#plt.plot(x,y)
plt.xlabel('Cities',fontsize=18)
plt.ylabel('Damage in INR',fontsize=18)
plt.title('Damage Analysis Graph')
plt.bar(x,y)
plt.show()
