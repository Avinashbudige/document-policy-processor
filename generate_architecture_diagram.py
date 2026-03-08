"""
Generate AWS Architecture Diagram for Document Policy Processor

This script creates a visual architecture diagram using the diagrams library.
Install: pip install diagrams

Usage: python generate_architecture_diagram.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.network import APIGateway
from diagrams.aws.storage import S3
from diagrams.aws.database import Dynamodb
from diagrams.aws.devtools import ECR
from diagrams.aws.management import Cloudwatch
from diagrams.aws.security import IAM
from diagrams.onprem.client import Users
from diagrams.onprem.compute import Server
from diagrams.programming.framework import React

# Diagram configuration
graph_attr = {
    "fontsize": "16",
    "bgcolor": "white",
    "pad": "0.5",
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.0"
}

node_attr = {
    "fontsize": "12",
    "height": "1.2",
    "width": "1.2"
}

edge_attr = {
    "fontsize": "10"
}

with Diagram(
    "Document Policy Processor - AWS Architecture",
    filename="document-policy-processor-architecture",
    direction="TB",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
    show=False
):
    
    # User
    user = Users("End User\n(Browser)")
    
    # Frontend
    with Cluster("Frontend Layer"):
        streamlit = Server("Streamlit Cloud\n(Python Web App)")
    
    # API Gateway
    with Cluster("API Gateway Layer"):
        api_gateway = APIGateway("API Gateway\n(REST API)\nbmi41mg6uf")
    
    # Lambda and Processing
    with Cluster("Compute Layer"):
        with Cluster("Lambda Container\n(3GB, 900s timeout)"):
            lambda_func = Lambda("DocumentPolicyProcessor\n(Python 3.11)")
            
            with Cluster("Processing Components"):
                text_extractor = Server("Text Extractor\n(Tesseract OCR)")
                policy_matcher = Server("Policy Matcher\n(Sentence Transformers)")
                llm_checker = Server("LLM Checker\n(Mistral AI)")
                rec_engine = Server("Recommendation\nEngine")
    
    # Storage Layer
    with Cluster("Storage Layer"):
        s3 = S3("S3 Bucket\ndocument-policy-\nprocessor-uploads")
        
        with Cluster("DynamoDB Tables"):
            dynamodb_policies = Dynamodb("Policies\nTable")
            dynamodb_jobs = Dynamodb("ProcessingJobs\nTable")
        
        ecr = ECR("ECR\nContainer\nRegistry")
    
    # External Services
    with Cluster("External Services"):
        mistral = Server("Mistral AI API\n(mistral-small-latest)")
    
    # Monitoring
    with Cluster("Monitoring & Logging"):
        cloudwatch = Cloudwatch("CloudWatch\nLogs & Metrics")
    
    # Security
    with Cluster("Security & IAM"):
        iam = IAM("IAM Roles\n& Policies")
    
    # Data Flow
    user >> Edge(label="HTTPS") >> streamlit
    streamlit >> Edge(label="REST API\nX-Api-Key") >> api_gateway
    api_gateway >> Edge(label="Lambda Proxy") >> lambda_func
    
    # Lambda to Storage
    lambda_func >> Edge(label="Get/Put\nDocuments") >> s3
    lambda_func >> Edge(label="Query/Update\nPolicies") >> dynamodb_policies
    lambda_func >> Edge(label="Query/Update\nJobs") >> dynamodb_jobs
    lambda_func >> Edge(label="Pull Image") >> ecr
    
    # Lambda to External
    lambda_func >> Edge(label="API Call\nExclusion Check") >> mistral
    
    # Processing Flow
    lambda_func >> text_extractor >> policy_matcher >> llm_checker >> rec_engine
    
    # Monitoring
    api_gateway >> Edge(label="Logs", style="dashed") >> cloudwatch
    lambda_func >> Edge(label="Logs & Metrics", style="dashed") >> cloudwatch
    s3 >> Edge(label="Metrics", style="dashed") >> cloudwatch
    dynamodb_policies >> Edge(label="Metrics", style="dashed") >> cloudwatch
    dynamodb_jobs >> Edge(label="Metrics", style="dashed") >> cloudwatch
    
    # Security
    lambda_func >> Edge(label="Assume Role", style="dashed") >> iam
    api_gateway >> Edge(label="Assume Role", style="dashed") >> iam

print("✅ Architecture diagram generated: document-policy-processor-architecture.png")
print("📁 Location: Current directory")
