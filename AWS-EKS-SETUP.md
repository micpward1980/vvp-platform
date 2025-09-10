# Complete AWS EKS Setup Guide for VVP Platform

## Prerequisites Checklist
- ✅ macOS with Homebrew installed
- ✅ kubectl installed (`brew install kubectl`)
- 🔲 AWS Account (free tier available)
- 🔲 AWS CLI installed and configured
- 🔲 eksctl installed

## Step 1: Create AWS Account

1. **Sign up at AWS**: https://aws.amazon.com/
   - Choose "Create a new AWS account"
   - Provide email, password, and account name
   - Enter payment information (required but free tier available)
   - Verify phone number and identity
   - Choose "Basic support - Free"

2. **Sign in to AWS Console**: https://console.aws.amazon.com/

## Step 2: Create IAM User for Programmatic Access

1. **Navigate to IAM**:
   - In AWS Console, search for "IAM" and click on it
   - Click "Users" in the left sidebar
   - Click "Create user"

2. **Configure User**:
   - User name: `vvp-deployment-user`
   - Check "Provide user access to the AWS Management Console" (optional)
   - Check "I want to create an IAM user"
   - Click "Next"

3. **Set Permissions**:
   - Choose "Attach policies directly"
   - Search and select these policies:
     - `AmazonEKSClusterPolicy`
     - `AmazonEKSWorkerNodePolicy`
     - `AmazonEKS_CNI_Policy`
     - `AmazonEC2ContainerRegistryReadOnly`
     - `IAMFullAccess` (for eksctl to create roles)
     - `AmazonEC2FullAccess` (for node groups)
   - Click "Next"

4. **Review and Create**:
   - Review settings
   - Click "Create user"

5. **Create Access Keys**:
   - Click on the newly created user
   - Go to "Security credentials" tab
   - Click "Create access key"
   - Choose "Command Line Interface (CLI)"
   - Check the confirmation box
   - Click "Create access key"
   - **IMPORTANT**: Copy both "Access key ID" and "Secret access key"

## Step 3: Install and Configure AWS CLI

1. **Install AWS CLI**:
```bash
brew install awscli
```

2. **Configure AWS CLI**:
```bash
aws configure
```
Enter when prompted:
- AWS Access Key ID: [paste your access key ID]
- AWS Secret Access Key: [paste your secret access key]
- Default region name: `us-west-2` (or your preferred region)
- Default output format: `json`

3. **Verify Configuration**:
```bash
aws sts get-caller-identity
```
Should return your user information.

## Step 4: Install eksctl

```bash
brew install eksctl
```

Verify installation:
```bash
eksctl version
```

## Step 5: Create EKS Cluster

1. **Create Cluster** (takes 15-20 minutes):
```bash
eksctl create cluster \
  --name vvp-cluster \
  --region us-west-2 \
  --nodegroup-name workers \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 3 \
  --managed
```

2. **Monitor Progress**:
The command will show progress. You'll see:
- Creating CloudFormation stack
- Creating EKS cluster
- Creating node group
- Configuring kubectl

3. **Verify Cluster**:
```bash
kubectl get nodes
```
Should show 2 worker nodes in "Ready" status.

## Step 6: Get Kubeconfig for GitLab

1. **Ensure kubectl is configured**:
```bash
kubectl config current-context
```
Should show your EKS cluster context.

2. **Get base64-encoded kubeconfig**:
```bash
cat ~/.kube/config | base64
```

3. **Copy the output** - you'll need this for GitLab CI/CD variable.

## Step 7: Configure GitLab CI/CD

1. **Go to GitLab project**: https://gitlab.com/micpward-group/vvp-platfom
2. **Navigate to**: Settings → CI/CD → Variables
3. **Add Variable**:
   - Key: `KUBE_CONFIG_B64`
   - Value: [paste the base64 kubeconfig from step 6]
   - Type: Variable
   - Flags: ✅ Masked, ✅ Protected

## Step 8: Create Merge Request and Deploy

1. **Create MR**: https://gitlab.com/micpward-group/vvp-platfom/-/merge_requests/new?merge_request%5Bsource_branch%5D=devin%2Fvvp-bootstrap

2. **MR Details**:
   - Title: VVP Platform Implementation - 6 FastAPI Microservices with Helm & CI/CD
   - Source: devin/vvp-bootstrap
   - Target: main

3. **Merge to Deploy**:
   - Once MR is approved, merge it
   - Pipeline will automatically trigger
   - Monitor at: https://gitlab.com/micpward-group/vvp-platfom/-/pipelines

## Step 9: Verify Deployment

1. **Check pods**:
```bash
kubectl -n vvp get pods
```

2. **Check services**:
```bash
kubectl -n vvp get svc
```

3. **Test claims API**:
```bash
kubectl port-forward -n vvp svc/claims-orchestrator 8080:80
```

In another terminal:
```bash
curl -X POST http://localhost:8080/claims \
  -H "Content-Type: application/json" \
  -d '{
    "policyId": "P-1001",
    "holderName": "Alex Driver",
    "vin": "1HGCM82633A004352",
    "lossDate": "2025-09-01T12:00:00Z",
    "lossType": "hail",
    "details": "Hail dents"
  }'
```

## Troubleshooting

### Common Issues

1. **AWS CLI not configured**:
   - Run `aws configure` again
   - Verify with `aws sts get-caller-identity`

2. **eksctl permissions error**:
   - Ensure IAM user has all required policies
   - Check AWS region matches in all commands

3. **Cluster creation fails**:
   - Check AWS service limits
   - Verify region has EKS service available
   - Try different instance types if t3.medium unavailable

4. **kubectl not connecting**:
   - Run: `aws eks update-kubeconfig --region us-west-2 --name vvp-cluster`

5. **Pipeline fails at deploy stage**:
   - Verify KUBE_CONFIG_B64 is set correctly
   - Check cluster is accessible: `kubectl get nodes`

### Cost Considerations

- **EKS Cluster**: ~$0.10/hour ($72/month)
- **EC2 Instances**: 2 × t3.medium ~$0.08/hour each ($120/month total)
- **Total**: ~$200/month (can be reduced with smaller instances)

### Cleanup (when done testing)

```bash
# Delete cluster (this will delete all resources)
eksctl delete cluster --name vvp-cluster --region us-west-2
```

## Timeline Estimate

- AWS Account Setup: 10-15 minutes
- IAM User Creation: 5 minutes
- CLI Installation/Config: 5 minutes
- EKS Cluster Creation: 15-20 minutes
- GitLab Configuration: 2 minutes
- Pipeline Deployment: 15-20 minutes
- **Total**: ~60-75 minutes

## Next Steps After Cluster is Ready

1. Create the GitLab MR using the provided URL
2. Set the KUBE_CONFIG_B64 variable in GitLab
3. Merge the MR to trigger deployment
4. Verify the VVP platform is running
5. Test the complete claims workflow

The VVP platform code is ready and waiting in the `devin/vvp-bootstrap` branch!
