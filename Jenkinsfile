pipeline {
    agent any

    options {
        timeout(time: 15, unit: 'MINUTES')
    }

    environment {
        COMPOSE_PROJECT_NAME = 'flask-mysql-ci'
        IMAGE_NAME = 'flask-mysql-app'
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
                    curl -fsL -d "body=jenkins-test" http://localhost:5000/add -o /dev/null
                    curl -fs http://localhost:5000/ | grep -q "jenkins-test"
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub',
                                                  usernameVariable: 'DH_USER',
                                                  passwordVariable: 'DH_PASS')]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                        docker build -t "$DH_USER/$IMAGE_NAME:$BUILD_NUMBER" -t "$DH_USER/$IMAGE_NAME:latest" .
                        docker push "$DH_USER/$IMAGE_NAME:$BUILD_NUMBER"
                        docker push "$DH_USER/$IMAGE_NAME:latest"
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker compose down -v || true'
            sh 'docker logout || true'
        }
    }
}
