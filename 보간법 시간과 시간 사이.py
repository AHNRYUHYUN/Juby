import pandas as pd
from datetime import timedelta
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response

from accountapp.models import Robot
from accountapp.serializer import RobotSerializer


class RobotViewSet(viewsets.ModelViewSet):
    queryset = Robot.objects.all()
    serializer_class = RobotSerializer

    def create(self, request, *args, **kwargs):
        """
        새 Robot 데이터를 POST로 받으면,
        - DB에 저장하고
        - (area, height)가 같은 이전 레코드와 새 레코드 사이에 보간된 중간 레코드 생성
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_instance = serializer.save()  # DB Insert

        # 보간 로직 실행
        self.create_midpoint_record(
            area=new_instance.area,
            height=new_instance.height,
            new_date=new_instance.date,
            new_temperature=new_instance.temperature
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def create_midpoint_record(self, area, height, new_date, new_temperature):
        """
        새 레코드가 들어온 후, 이전 레코드와 새 레코드 사이의 중간 시간에 보간된 레코드를 생성한다.

        Parameters:
            area (str): 지역
            height (str): 높이
            new_date (datetime): 새 레코드의 날짜
            new_temperature (float): 새 레코드의 온도
        """
        # 1. new_date보다 과거인 가장 최근 레코드 찾기
        older_instance = (
            Robot.objects
            .filter(area=area, height=height, date__lt=new_date)
            .order_by('-date')
            .first()
        )

        if not older_instance:
            # 이전 레코드가 없으면 보간할 구간이 없음
            return

        older_date = older_instance.date
        older_temperature = older_instance.temperature

        # 2. 이전 레코드와 새 레코드 사이의 시간 차이 계산
        delta = new_date - older_date
        total_seconds = delta.total_seconds()

        if total_seconds <= 0:
            # 시간이 이전과 같거나 뒤로 돌아간 경우 보간하지 않음
            return

        # 3. 중간 시간 계산
        midpoint = older_date + timedelta(seconds=total_seconds / 2)

        # 4. 중간 시간에 이미 레코드가 존재하는지 확인
        if Robot.objects.filter(area=area, height=height, date=midpoint).exists():
            # 이미 중간 시간에 레코드가 존재하면 생략
            return

        # 5. 보간된 온도값 계산 (선형 보간)
        interpolated_temperature = (older_temperature + new_temperature) / 2

        # 6. 보간된 레코드 생성
        interpolated_record = Robot(
            area=area,
            height=height,
            temperature=interpolated_temperature,
            humidity=None,  # 필요 시 다른 센서값도 보간 가능
            soil_temperature=None,
            soil_humidity=None,
            date=midpoint,
            member=older_instance.member,  # 이전 레코드의 member와 farm을 사용
            farm=older_instance.farm
        )

        # 7. DB에 저장
        interpolated_record.save()



#1분 이상 차이 일때 보간법
class RobotViewSet(viewsets.ModelViewSet):
    queryset = Robot.objects.all()
    serializer_class = RobotSerializer

    def create(self, request, *args, **kwargs):
        """
        새 Robot 데이터를 POST로 받으면,
        - DB에 저장하고
        - (area, height)가 같은 이전 레코드와 새 레코드 사이에 보간된 중간 레코드 생성
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_instance = serializer.save()  # DB Insert

        # 보간 로직 실행
        self.create_interpolated_records(
            area=new_instance.area,
            height=new_instance.height,
            new_date=new_instance.date,
            new_temperature=new_instance.temperature
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def create_interpolated_records(self, area, height, new_date, new_temperature, interval_minutes=1):
        """
        새 레코드가 들어온 후, 이전 레코드와 새 레코드 사이에 보간된 레코드를 생성한다.

        Parameters:
            area (str): 지역
            height (str): 높이
            new_date (datetime): 새 레코드의 날짜
            new_temperature (float): 새 레코드의 온도
            interval_minutes (int): 보간 간격(분 단위)
        """
        # 1. new_date보다 과거인 가장 최근 레코드 찾기
        older_instance = (
            Robot.objects
            .filter(area=area, height=height, date__lt=new_date)
            .order_by('-date')
            .first()
        )

        if not older_instance:
            # 이전 레코드가 없으면 보간할 구간이 없음
            return

        older_date = older_instance.date
        older_temperature = older_instance.temperature

        # 2. 이전 레코드와 새 레코드 사이의 시간 차이 계산
        delta = new_date - older_date
        total_minutes = int(delta.total_seconds() // 60)

        if total_minutes <= interval_minutes:
            # 간격이 너무 짧아서 보간할 필요가 없음
            return

        # 3. 보간 간격으로 날짜 리스트 생성
        interpolated_times = [
            older_date + timedelta(minutes=i)
            for i in range(interval_minutes, total_minutes, interval_minutes)
        ]

        # 4. 보간된 온도값 계산
        interpolated_temperatures = [
            older_temperature + (new_temperature - older_temperature) * (i / total_minutes)
            for i in range(interval_minutes, total_minutes, interval_minutes)
        ]

        # 5. 기존에 존재하는 중간 레코드 확인 (중복 방지)
        existing_dates = Robot.objects.filter(
            area=area,
            height=height,
            date__in=interpolated_times
        ).values_list('date', flat=True)

        # 6. 보간된 레코드 생성
        new_interpolated_records = []
        for time, temp in zip(interpolated_times, interpolated_temperatures):
            if time in existing_dates:
                # 이미 해당 시간에 레코드가 존재하면 생략
                continue
            new_interpolated_records.append(Robot(
                area=area,
                height=height,
                temperature=temp,
                humidity=None,  # 필요 시 다른 센서값도 보간 가능
                soil_temperature=None,
                soil_humidity=None,
                date=time,
                member=older_instance.member,  # 이전 레코드의 member와 farm을 사용
                farm=older_instance.farm
            ))

        # 7. DB에 한꺼번에 저장
        if new_interpolated_records:
            Robot.objects.bulk_create(new_interpolated_records, ignore_conflicts=True)





            #todo: 토양 데이터는 삭제하는거로 수정