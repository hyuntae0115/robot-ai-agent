# 시스템 구조

## Project Title

AI 에이전트를 활용한 로봇 가공

## Project Goal

본 프로젝트는 사람의 음성 가공 명령을 AI 에이전트가 해석하여 로봇이 수행 가능한 기계명령어로 변환하고, 카메라를 통해 작업 환경을 인식하며, 사람 접근시 모든 로봇 명령을 정지시키는 안전 인식형 로봇 가공 에이전틱 시스템을 구축하는 것을 목표로 한다.

## input

voice command
gui command
text command

## output

vaildated maching command JSON
rejection reason if the command is unsafe or imcomlpete
clarification question if the command is ambiguous

## Overall Pipeline

```text
User
  ↓
Voice Input / GUI
  ↓
Speech-to-Text
  ↓
Natural Language Command Parser
  ↓
Structured Command Schema
  ↓
Command Validator
  ↓
Task Planner
  ↓
Safety Checker
  ↓
Robot Command Generator
  ↓
Robot Controller