###############################################################################
##
##  Copyright (C) 2011-2014 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

from autobahn.wamp.exception import ApplicationError
from autobahn.wamp.router import Router

class MyRouter(Router):

   def validate(self, payload_type, uri, args, kwargs):
      print("MyRouter.validate: {} {} {} {}".format(payload_type, uri, args, kwargs))

      if payload_type == 'event' and uri == 'com.myapp.topic1':
         if len(args) == 1 and type(args[0]) == int and args[0] % 2 == 0 and kwargs is None:
            print("event payload validated for {}".format(uri))
         else:
            raise ApplicationError(ApplicationError.INVALID_ARGUMENT, "invalid event payload for topic {} - must be a single integer".format(uri))



if __name__ == '__main__':

   import sys, argparse

   from twisted.python import log
   from twisted.internet.endpoints import serverFromString

   ## parse command line arguments
   ##
   parser = argparse.ArgumentParser()

   parser.add_argument("-d", "--debug", action = "store_true",
                       help = "Enable debug output.")

   parser.add_argument("--endpoint", type = str, default = "tcp:8080",
                       help = 'Twisted server endpoint descriptor, e.g. "tcp:8080" or "unix:/tmp/mywebsocket".')

   args = parser.parse_args()
   log.startLogging(sys.stdout)

   ## we use an Autobahn utility to install the "best" available Twisted reactor
   ##
   from autobahn.twisted.choosereactor import install_reactor
   reactor = install_reactor()
   print("Running on reactor {}".format(reactor))


   ## create a WAMP router factory
   ##
   from autobahn.wamp.router import RouterFactory
   router_factory = RouterFactory()
   router_factory.router = MyRouter


   ## create a WAMP router session factory
   ##
   from autobahn.twisted.wamp import RouterSessionFactory
   session_factory = RouterSessionFactory(router_factory)


   ## create a WAMP-over-WebSocket transport server factory
   ##
   from autobahn.twisted.websocket import WampWebSocketServerFactory
   transport_factory = WampWebSocketServerFactory(session_factory, debug = args.debug)
   transport_factory.setProtocolOptions(failByDrop = False)


   ## start the server from an endpoint
   ##
   server = serverFromString(reactor, args.endpoint)
   server.listen(transport_factory)


   ## now enter the Twisted reactor loop
   ##
   reactor.run()
