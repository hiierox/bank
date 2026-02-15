{{/*
Expand the name of the chart.
*/}}
{{- define "user-data-service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "user-data-service.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "user-data-service.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "user-data-service.labels" -}}
helm.sh/chart: {{ include "user-data-service.chart" . }}
{{ include "user-data-service.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "user-data-service.selectorLabels" -}}
app.kubernetes.io/name: {{ include "user-data-service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "user-data-service.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "user-data-service.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/* Имя Deployment */}}
{{- define "user-data-service.fullname.release" -}}
{{ .Release.Name }}
{{- end }}

{{/* Лейблы для ресурсов */}}
{{- define "user-data-service.selectorLabels.custom" -}}
app: user-data-service
student: {{ .Values.student.name | quote }}
{{- end }}

{{/* Имя configmap */}}
{{- define "user-data-service.configmap.name" -}}
user-data-service-config-{{ .Values.student.name | lower }}
{{- end }}
