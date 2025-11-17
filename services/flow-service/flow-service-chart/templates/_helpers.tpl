{{/*
Expand the name of the chart.
*/}}
{{- define "flow-service-chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "flow-service-chart.fullname" -}}
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
{{- define "flow-service-chart.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "flow-service-chart.labels" -}}
helm.sh/chart: {{ include "flow-service-chart.chart" . }}
{{ include "flow-service-chart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "flow-service-chart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "flow-service-chart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "flow-service-chart.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "flow-service-chart.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}


{{/* Имя Deployment */}}
{{- define "flow-selection-service.fullname.release" -}}
{{ .Release.Name }}
{{- end }}

{{/* Лейблы для ресурсов */}}
{{- define "flow-selection-service.selectorLabels.custom" -}}
app: flow-selection-service
student: {{ .Values.student.name | quote }}
{{- end }}

{{/* Имя configmap */}}
{{- define "flow-selection-service.configmap.name" -}}
flow-selection-service-config-{{ .Values.student.name | lower }}
{{- end }}

{{/* Имя контейнера */}}
{{- define "flow-selection-service-container.name" -}}
flow-selection-service-container
{{- end }}
