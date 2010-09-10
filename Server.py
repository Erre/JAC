from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet  import reactor
from twisted.internet.protocol import ServerFactory
import time


class ChatConnection(LineOnlyReceiver):

	hostlist = []
                            
### Functions -- Begin

	def sendLine(self, line):
		self.transport.write(line + '\n')

	def print_time(self):
		return time.strftime("[%H:%M] ", time.localtime(time.time()))

	def name(self):
		self.nick = self.transport.getPeer().host
		return self.nick
			
	def quit(self):
		self.transport.loseConnection()
                print self.print_time() + "Connection quit by", self.name()
                self.factory.send_to_all(self.print_time() + self.name() + " has quit")
                self.factory.clientlist.remove(self)
		self.hostlist.remove(self.name())

	def help(self):
		self.sendLine("\n\t Pychat help: \n")
		self.sendLine("\t /nick (your nick) to change your nick")
		self.sendLine("\t /quit to close the connection")
		self.sendLine("\t /list to see the chat users\n")

	def list(self):
		self.sendLine(self.print_time() + "Online users: \n\t" + str(self.hostlist))

### Functions -- End	
	
	commands = ["/nick", "/help", "/quit", "/list"]

	switch = {'/help' : help,
		  '/quit' : quit,
		  '/list' : list }

	def connectionMade(self):
                print  self.print_time() + "New connection from " + self.name()
                self.sendLine("Type /help to see the help")
                self.factory.send_to_all(self.print_time() + self.name() + " has joined the conversation")
                self.factory.clientlist.append(self)
                self.hostlist.append(self.name())

        def connectionLost(self, reason):
                print self.print_time() + "Connection lost by", self.name()
                self.factory.send_to_all(self.print_time() + self.name() + " has lost the connection")
                self.factory.clientlist.remove(self)
                self.hostlist.remove(self.name())

		  
    	def lineReceived(self, line):
		if line[:5] in self.commands:
			pass
		else:
			self.factory.send_to_all(self.print_time() + self.name() + ":  " + line)

		if line[:5] == "/nick":
			self.factory.send_to_all(self.print_time() + self.name() + " has changed his name in " + line[6:])
	                self.hostlist.remove(self.name())
               		self.name = line[5:].strip
               		self.hostlist.append(self.name())

		for i in self.switch.keys():
			if line[:5] == i:
				cmd = self.switch[i]
				cmd(self) 
		
            	 
class Chat(ServerFactory):
     
    	protocol = ChatConnection
    
    	def __init__(self): 
       		 self.clientlist = []
    
    	def send_to_all(self, mex):
		for host in self.clientlist:
			host.sendLine(mex)


print "Waiting connection from clients..."
main = Chat()
reactor.listenTCP(8000, main)
reactor.run()
