{{- define "vvp.deployment" -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .name }}
  namespace: {{ .Release.Namespace }}
  labels: { app: {{ .name }} }
spec:
  replicas: {{ .replicas }}
  selector:
    matchLabels: { app: {{ .name }} }
  template:
    metadata:
      labels: { app: {{ .name }} }
    spec:
      containers:
        - name: {{ .name }}
          image: "{{ .image.repository }}:{{ .image.tag }}"
          imagePullPolicy: IfNotPresent
          ports: [{containerPort: 8000}]
          env:
            - name: SERVICE_NAME
              value: "{{ .name }}"
            - name: ORCH_VERIFICATION_URL
              value: "{{ $.Values.commonEnv.ORCH_VERIFICATION_URL }}"
            - name: ORCH_VALUATION_URL
              value: "{{ $.Values.commonEnv.ORCH_VALUATION_URL }}"
            - name: ORCH_PAYMENT_URL
              value: "{{ $.Values.commonEnv.ORCH_PAYMENT_URL }}"
            - name: ORCH_AUDIT_URL
              value: "{{ $.Values.commonEnv.ORCH_AUDIT_URL }}"
            - name: ORCH_VIN_URL
              value: "{{ $.Values.commonEnv.ORCH_VIN_URL }}"
          readinessProbe:
            httpGet: { path: /ready, port: 8000 }
            initialDelaySeconds: 5
            periodSeconds: 5
          livenessProbe:
            httpGet: { path: /health, port: 8000 }
            initialDelaySeconds: 10
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: {{ .name }}
  namespace: {{ .Release.Namespace }}
  labels: { app: {{ .name }} }
spec:
  type: ClusterIP
  selector: { app: {{ .name }} }
  ports:
    - name: http
      port: 80
      targetPort: 8000
{{- end -}}
