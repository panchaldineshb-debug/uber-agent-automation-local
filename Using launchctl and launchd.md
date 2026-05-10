# Using launchctl

I have a lot of scripts that automate the boring parts of my life. Recently an article was posted about one system administrator who automated everything down to scripting the coffee maker to produce cups of coffee for him. I don’t go quite that far with my automation, but it inspired me to write about a lesser known tool in OSX - launchd and its interfacing agent: launchctl.

Great! Let's start with the com.sarabilabs.rideagent.plist file and document it based on the information provided in the link you shared.                                

Every launchd service is configured using a plist file. Multiple options can be specified in the plist file. The documentation for those options can be found in the man pages (gasp!) under the launchd.plist entry. These configuration files usually live in ~/Library/LaunchAgents. If your user has no custom services yet running via launchd, you will need to create that folder. A benefit of this is that files for all of the daemons live in one location, which makes it easy to organize and keep track of the different services.


Documentation for com.sarabilabs.rideagent.plist                                                                                                                         

File Path:                                                                                                                                                               

                                                                                                                                                                         
com.sarabilabs.rideagent.plist                                                                                                                                           
                                                                                                                                                                         

Purpose:                                                                                                                                                                 

This .plist file is used to configure a Launchd agent that runs a Python script (local_worker.py) at startup and keeps it running continuously.                          

Key Components:                                                                                                                                                          

 1 Label:                                                                                                                                                                
    • Key: Label                                                                                                                                                         
    • Value: com.sarabilabs.rideagent                                                                                                                                    
    • Description: A unique identifier for the job, following the reverse domain naming convention.                                                                      
 2 ProgramArguments:                                                                                                                                                     
    • Key: ProgramArguments                                                                                                                                              
    • Value:                                                                                                                                                             
                                                                                                                                                                         
                                                                                                                                                                         
      <array>                                                                                                                                                            
                                                                                                                                                                         
          <string>/Users/panchaldineshb/Public/Sameer/uber-agent-automation-local/.venv/bin/python</string>                                                              
                                                                                                                                                                         
          <string>/Users/panchaldineshb/Public/Sameer/uber-agent-automation-local/agents/local_worker.py</string>                                                        
                                                                                                                                                                         
                                                                                                                                                                         
                                                                                                                                                                         
    • Description: Specifies the command to run. In this case, it runs the Python script local_worker.py using a virtual environment's Python interpreter.               
 3 RunAtLoad:                                                                                                                                                            
 3 RunAtLoad:                                                                                                                                                            
    • Value: <true/>                                                                                                                                                     
    • Description: Indicates that the job should be started immediately when loaded.                                                                                     
 4 KeepAlive:                                                                                                                                                            
    • Key: KeepAlive                                                                                                                                                     
    • Value: <true/>                                                                                                                                                     
    • Description: Ensures that the job is kept running and restarted if it exits.                                                                                       
 5 WorkingDirectory:                                                                                                                                                     
    • Key: WorkingDirectory                                                                                                                                              
    • Value: /Users/panchaldineshb/Public/Sameer/uber-agent-automation-local                                                                                             
    • Description: Sets the working directory for the job, which is where the script will run.                                                                           
 6 StandardOutPath:                                                                                                                                                      
    • Key: StandardOutPath                                                                                                                                               
    • Value: /Users/panchaldineshb/Public/Sameer/uber-agent-automation-local/logs/stdout.log                                                                             
    • Description: Specifies the file path for standard output logs.                                                                                                     
 7 StandardErrorPath:                                                                                                                                                    
    • Key: StandardErrorPath                                                                                                                                             
    • Value: /Users/panchaldineshb/Public/Sameer/uber-agent-automation-local/logs/stderr.log                                                                             
    • Description: Specifies the file path for standard error logs.                                                                                                      
 8 EnvironmentVariables:                                                                                                                                                 
    • Key: EnvironmentVariables                                                                                                                                          
    • Value:                                                                                                                                                             
                                                                                                                                                                         
                                                                                                                                                                         
      <dict>                                                                                                                                                             
                                                                                                                                                                         
          <key>PYTHONUNBUFFERED</key>                                                                                                                                    
                                                                                                                                                                         
          <string>1</string>                                                                                                                                             
                                                                                                                                                                         
          <key>PYTHONPATH</key>                                                                                                                                          
                                                                                                                                                                         
          <string>/Users/panchaldineshb/Public/Sameer/uber-agent-automation-local</string>                                                                               
                                                                                                                                                                         
      </dict>                                                                                                                                                            
                                                                                                                                                                         
    • Description: Sets environment variables for the job. PYTHONUNBUFFERED ensures that Python output is not buffered, and PYTHONPATH sets the Python path to include   
      the project directory.                                                                                                                                             

How to Use:                                                                                                                                                              

 1 Load the Agent:                                                                                                                                                       
    • To load the agent and start it immediately, use the following command:                                                                                             
                                                                                                                                                                         
                                                                                                                                                                         
      launchctl load /path/to/com.sarabilabs.rideagent.plist                                                                                                             
                                                                                                                                                                         
 2 Unload the Agent:                                                                                                                                                     
    • To stop and unload the agent, use the following command:                                                                                                           
                                                                                                                                                                         
                                                                                                                                                                         
      launchctl unload /path/to/com.sarabilabs.rideagent.plist                                                                                                           
                                                                                                                                                                         
 3 Start the Agent Manually:                                                                                                                                             
    • If you want to start the agent manually without waiting for it to be loaded at boot or login, use the following command:                                           
                                                                                                                                                                         
                                                                                                                                                                         
      launchctl start com.sarabilabs.rideagent                                                                                                                           
                                                                                                                                                                         

Additional Notes:                                                                                                                                                        

 • Ensure that the paths specified in ProgramArguments, WorkingDirectory, StandardOutPath, and StandardErrorPath are correct and accessible.                             
 • The agent will run as the user who loaded it, so ensure that the user has the necessary permissions to execute the script and write to the log files.                 

If there are any other .plist files or additional configuration steps you would like to include in the documentation, please let me know!                                

