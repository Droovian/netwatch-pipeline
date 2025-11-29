pipeline {
    agent { label 'Home-Network-Scanner' }
    
    triggers {
        cron('H * * * *') 
    }

    environment {
        // Keep secrets here or use Jenkins Credentials Binding for higher security
        DB_HOST = credentials('netwatch-db-host') 
        DB_PASS = credentials('netwatch-db-pass')
        DB_USER = 'admin'
        DB_NAME = 'netwatch'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'ls -R' 
            }
        }

        stage('Collect Data') {
            parallel {
                stage('Map Network') { 
                    steps { 
                        // Scan local subnet
                        sh 'nmap -sn 192.168.0.0/24 -oX scan.xml' 
                    } 
                }
                stage('Check Speed') { 
                    steps { 
                        sh 'speedtest-cli --secure --json > speed.json' 
                    } 
                }
            }
        }
        
        stage('Process & Upload') {
            steps {
                sh 'python3 scripts/monitor.py'
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'scan.xml, speed.json', allowEmptyArchive: true
            cleanWs() // Clean up workspace to save disk space
        }
    }
}
