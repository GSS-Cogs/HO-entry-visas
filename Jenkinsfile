pipeline {
    agent {
        label 'master'
    }
    triggers {
        upstream(upstreamProjects: '../Reference/ref_migration',
                 threshold: hudson.model.Result.SUCCESS)
    }
    stages {
        stage('Clean') {
            steps {
                sh 'rm -rf out'
            }
        }
        stage('Transform') {
            agent {
                docker {
                    image 'cloudfluff/databaker'
                    reuseNode true
                }
            }
            steps {
                sh "jupyter-nbconvert --output-dir=out --ExecutePreprocessor.timeout=None --execute 'main.ipynb'"
            }
        }
        stage('Test') {
            agent {
                docker {
                    image 'cloudfluff/csvlint'
                    reuseNode true
                }
            }
            steps {
                script {
                    sh "csvlint -s https://github.com/ONS-OpenData/ref_migration/raw/master/codelist-schema.json out/ho-application-categories.csv"
                    sh "csvlint -s https://github.com/ONS-OpenData/ref_migration/raw/master/codelist-schema.json out/ho-countries.csv"
                }
            }
        }
        stage('Upload draftset') {
            steps {
                script {
                    jobDraft.replace()
                    uploadCodelist('out/ho-application-categories.csv', 'HO Application Category')
                    uploadCodelist('out/ho-countries.csv', 'HO Citizenship')
                    uploadTidy(['out/entry_visas.csv'],
                               'https://github.com/ONS-OpenData/ref_migration/raw/master/columns.csv')
                }
            }
        }
        stage('Publish') {
            steps {
                script {
                    jobDraft.publish()
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts 'out/*'
        }
        success {
            build job: '../GDP-tests', wait: false
        }
    }
}
