import matplotlib.pyplot as plt
x=['Bangalore','Chennai','Kochi','Panaji']
y=[100,900,600,500]
#plt.plot(x,y)
plt.xlabel('Cities',fontsize=14)
plt.ylabel('Damage in INR(K)',fontsize=14)
plt.title('Damage Analysis Graph',fontsize=14)
plt.bar(x,y)
plt.show()
