pipeline {
    agent any

    options {
        timeout(time: 15, unit: 'MINUTES')
    }

    environment {
        COMPOSE_PROJECT_NAME = 'flask-mysql-ci'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh 'docker compose build'
            }
        }

        stage('Start app') {
            steps {
                sh 'docker compose up -d'
            }
        }

        stage('Smoke test') {
            steps {
                sh '''
                    for i in $(seq 1 30); do
                        if curl -fs http://localhost:5000/health; then break; fi
                        sleep 2
                    done
                    curl -fs http://localhost:5000/health
                    curl -fsL -X POST -d "body=jenkins-test" http://localhost:5000/add -o /dev/null
                    curl -fs http://localhost:5000/ | grep -q "jenkins-test"
                '''
            }
        }
    }

    post {
        always {
            sh 'docker compose down -v || true'
        }
    }
}