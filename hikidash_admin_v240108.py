#성하 포크 test~
# 라이브러리 설치 안되어있으면 설치, streamlit 최신버전으로 업그레이드 필수! 안하면 st.container()에 border표기 안됨
# !pip install streamlit-option-menu
# !pip install streamlit-elements==0.1.*
# !pip install -U hydralit_components
# !pip install streamlit-pills
# !pip install streamlit-calendar # 안쓰는 라이브러리..캘린더

# 라이브러리 불러오기
import pandas as pd
import streamlit as st
import numpy as np
import datetime
import altair as alt

import json

from  PIL import Image
import requests
import folium
from streamlit_folium import st_folium

from streamlit_option_menu import option_menu
from streamlit_elements import elements, mui, html, dashboard, nivo
import hydralit_components as hc
from streamlit_pills import pills

# import webbrowser
# 언젠간 쓸지도 모르지만 안쓰는 라이브러리
# from streamlit_calendar import calendar
# from urllib.parse import quote
# import ssl
# from urllib.request import urlopen
# import streamlit.components.v1 as html
# from streamlit_chat import message
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity
# -------------------- ▼ Geocoding API로 주소를 위도, 경도로 변환 ▼ --------------------

# # 주소 -> 위도, 경도 변환을 위한 Geocoding API 호출
# def geocode_address(address, api_key):
#     url = "https://maps.googleapis.com/maps/api/geocode/json"
#     params = {"address": address, "key": api_key}
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         data = response.json()
#         if data['status'] == 'OK' and data['results']:
#             location = data['results'][0]['geometry']['location']
#             return location['lat'], location['lng']
#     return None, None

# # Read your CSV file
# df = pd.read_csv('original.csv')

# # Prepare lists to hold the geocoded coordinates
# latitudes = []
# longitudes = []

# # Your Google Geocoding API key
# api_key = 'AIzaSyDiHRIVC8Sw2wRa3y9FbY8AeDUUh1Lb_C8'  # Replace with your actual API key

# # Iterate over the addresses in the DataFrame
# for address in df['주소']:
#     lat, lng = geocode_address(address, api_key)
#     latitudes.append(lat)
#     longitudes.append(lng)
    
# # Add the latitude and longitude as new columns to the DataFrame
# df['latitude'] = latitudes
# df['longitude'] = longitudes

# # Save the updated DataFrame back to a new CSV
# df.to_csv('updated_conversation_history.csv', index=False)

# -------------------- ▲ Geocoding API로 주소를 위도, 경도로 변환 ▲ --------------------

# -------------------- ▼ Streamlit 웹 화면 구성 START ▼ --------------------

## 레이아웃 구성하기
st.set_page_config(
    page_title="어른이집 선생님용",
    page_icon="🐣",
    layout="wide",
    initial_sidebar_state="expanded"
)

## -------------------------------------------------------------------------------------

## -------------------- ▼ 필요한 함수 ▼ --------------------
# 나이 계산하기
def calculate_age(birthdate):
    # 현재 날짜
    current_date = datetime.datetime.now()
    
    # 생년월일 문자열을 datetime 객체로 변환
    birthdate_obj = datetime.datetime.strptime(birthdate, "%Y-%m-%d")
    
    # 나이 계산
    age = current_date.year - birthdate_obj.year - ((current_date.month, current_date.day) < (birthdate_obj.month, birthdate_obj.day))
    
    return age
## -------------------------------------------------------------------------------------

# 멀티 페이지
# page1 내용물 구성하기 
def main_page():
    st.sidebar.header('개별 관리')
    st.sidebar.markdown('##### 청년 정보를 입력하면, 데이터셋으로 저장합니다.')
    
    ## 제목 넣기
    st.markdown("## 개별 관리")
    
    # 정보 조회    
    df = pd.read_csv('original4.csv')
    # 불필요한 정보 제거
    df.drop(['위도', '경도'], axis=1, inplace=True)
    # 이름만 뽑아내서 정보 찾기
    cols = st.columns([0.12, 0.12, 0.08, 0.1, 0.08, 0.3])
    with cols[0]:
        names = df['이름'].unique()
        selected_name = st.selectbox('',
                                     names,
                                     index=None,
                                     placeholder="이름",
                                     label_visibility='collapsed')
    with cols[1]:
        times = df['회차'].unique()
        max_times = df['회차'].max()
        selected_times = st.selectbox('',
                                      times,
                                      index=None,
                                      placeholder='회차',
                                      label_visibility='collapsed')
    with cols[2]:
        on = st.toggle('나이:')
    with cols[3]:
        if on:
            if selected_name is not None:
                birthdate = df.loc[df['이름'] == selected_name, '생년월일'].iloc[0]
                age = calculate_age(birthdate)
                st.markdown(f'{age}세')
    with cols[4]:
        on2 = st.toggle('주소:')
    with cols[5]:
        if on2:
            if selected_name is not None:
                address = df.loc[df['이름'] == selected_name, '주소'].iloc[0]
                st.markdown(f'{address}')
    
    tab1, tab2, tab3, tab4 = st.tabs(['현재 상태', '챗봇 대화 내역', '진행 상황', '특이사항'])
    with tab1:
        st.markdown(f"##### {selected_name}님의 현재 상태")
        
        # 불필요한 정보 제거
        selected_df = df.loc[df['이름'] == selected_name]
        selected_df = selected_df.drop(columns=['이름', '생년월일', '주소'])
        if selected_times is not None:
            selected_df = selected_df[selected_df['회차'] == selected_times]
        with st.expander('고립/은둔 상태 결과 차트', expanded=True):
            st.dataframe(selected_df, hide_index=True)


        # 대화 내역을 분석해 대상자의 상태를 표시(가정)    

        cols = st.columns([0.4, 0.6])
        with cols[0]:
            if selected_name is not None:
                # 진행 상황, 카드 색 커스텀
                theme_bad = {'bgcolor': '#FFF0F0','title_color': '#ff4b4b','content_color': '#ff4b4b','icon_color': '#ff4b4b', 'icon': 'fa fa-times-circle'}
                theme_neutral = {'bgcolor': '#ffebd8','title_color': '#31333f','content_color': '#ff5e03','icon_color': '#ff5e03', 'icon': 'fa fa-question-circle'}
                theme_good = {'bgcolor': '#EFF8F7','title_color': 'green','content_color': 'green','icon_color': 'green', 'icon': 'fa fa-check-circle'}

                # 고립 은둔 점수를 element로 두고, default값은 최신 회차
                if selected_times is None:
                    element = selected_df.loc[selected_df['회차'] == max_times, 'Total(/116)'].values[0].tolist()
                else:
                    element = selected_df.loc[selected_df['회차'] == selected_times, 'Total(/116)'].values[0].tolist()

                if element < 45:
                    # can just use 'good', 'bad', 'neutral' sentiment to auto color the card
                    hc.info_card(title=f'정상 {element}', content='고립/은둔 점수가 기준치보다 낮습니다!',
                                 sentiment='good',
                                 bar_value=element,
                                 icon_size="2.4rem",
                                 title_text_size="2rem",
                                 content_text_size="1rem")

                elif element >= 85:
                    hc.info_card(title=f'심각 {element}',
                                 content='고립/은둔 점수가 매우 높습니다. 대면 관리가 필요합니다.',
                                 bar_value=element, 
                                 icon_size="2.4rem",
                                 title_text_size="2rem", 
                                 content_text_size="1rem", 
                                 theme_override=theme_bad)
                elif (element < 85) & (element >= 65):
                    hc.info_card(title=f'경계 {element}', 
                                 content='고립/은둔 점수가 다소 높습니다. 세심한 관찰이 필요합니다.', 
                                 key='sec', 
                                 theme_override=theme_neutral, 
                                 icon_size="2.4rem",
                                 title_text_size="2rem", 
                                 content_text_size="1rem", 
                                 bar_value=element)
                else:
                    #customise the the theming for a neutral content
                    hc.info_card(title=f'주의 {element}',
                                 content='고립/은둔 점수가 기준치보다 조금 높습니다.',
                                 sentiment='neutral',
                                 icon_size="2.4rem",
                                 title_text_size="2rem", 
                                 content_text_size="1rem", 
                                 bar_value=element)

                #대상자의 고립/은둔 점수 변화도 그래프로 그리기
                with st.container(border=True):
                    st.markdown('###### 회차별 고립/은둔 점수 변화도(총 116점)')
                    all_chart = alt.Chart(df.loc[df['이름'] == selected_name]).mark_line(
                        point=alt.OverlayMarkDef(size=80, filled=False, fill="white")
                    ).encode(
                        x=alt.X('회차', axis=alt.Axis(format='d')),
                        y=alt.Y('Total(/116)', axis=alt.Axis(title=None), scale=alt.Scale(domain=[0, 120])),
                        tooltip=[alt.Tooltip('회차:O', title='회차'), alt.Tooltip('Total(/116):Q', title='점수')],
                        color=alt.value("#61cdbb")
                    ).properties(
                        height=290,
                    )
                    
                    if selected_times is not None:
                        dot_chart = alt.Chart(selected_df).mark_line(
                            point=alt.OverlayMarkDef(size=150, filled=True)
                        ).encode(
                            x=alt.X('회차', axis=alt.Axis(format='d')),
                            y=alt.Y('Total(/116)', axis=alt.Axis(title=None), scale=alt.Scale(domain=[0, 120])),
                            tooltip=[alt.Tooltip('회차:O', title='회차'), alt.Tooltip('Total(/116):Q', title='점수')],
                            color=alt.value("#61cdbb")
                        ).properties(
                            height=290,
                        )
                        combined_chart = all_chart + dot_chart
                        st.altair_chart(combined_chart, use_container_width=True)
                    else:
                        st.altair_chart(all_chart, use_container_width=True)

        with cols[1]:
            # 스탯 그래프 그리기
            stat_df = df.copy()
            stat_df['불안도'] = (stat_df['Emotional Support(/24)'] + 2 * stat_df['Motivation(/16)']) / 56 * 100
            stat_df['자존감 결여도'] = stat_df['Emotional Support(/24)'] / 24 * 100
            stat_df['정신적 고립도'] = stat_df['Socialization(/40)'] / 40 * 100
            stat_df['우울증상도'] = stat_df['Motivation(/16)'] / 16 * 100
            stat_df['공간적 고립도'] = stat_df['Isolation(/36)'] / 36 * 100
            stat_df = stat_df[['이름', '회차', '불안도', '자존감 결여도', '정신적 고립도', '우울증상도', '공간적 고립도']]
            stat_df2 = stat_df.loc[stat_df['이름'] == selected_name]

            if selected_times is None:
                stat = stat_df2.loc[stat_df2['회차']==max_times].copy()
            else:
                stat = stat_df2.loc[stat_df2['회차']==selected_times].copy()

            stat_melt = pd.melt(stat, id_vars = ['이름', '회차'])
            stat_melt = stat_melt.drop(columns=['이름', '회차'])
            stat_melt = stat_melt.to_dict(orient='records')
            
            if selected_name is not None:
                container = st.container(border=True)
            else:
                container = st.container()
                
            with container:
                with elements("nivo_charts"):
                    with mui.Box(sx={'height': 500}):
                        nivo.Radar(
                            data=stat_melt,
                            keys=['value'],
                            indexBy='variable',
                            valueFormat=">-.2f",
                            margin={ "top": 70, "right": 80, "bottom": 40, "left": 80 },
                            borderColor={ "from": "color" },
                            gridLabelOffset=25,
                            gridShape="linear",
                            dotSize=10,
                            dotColor={ "theme": "background" },
                            dotBorderWidth=2,
                            motionConfig="wobbly",
                            theme={
                                "background": "#FFFFFF",
                                "textColor": "#31333F",
                                "tooltip": {
                                    "container": {
                                        "background": "#FFFFFF",
                                        "color": "#31333F",
                                    }
                                }
                            }
                        )
                        
    with tab2:
        # 대화내역 불러오기, 요약하기(요약은 구현x 임의로)
        conv_hist = pd.read_csv('conversation_history.csv')
        st.markdown(f"##### {selected_name}님과 챗봇의 대화 내역")
        st.write(conv_hist)

        st.info("대화 내역 요약")
        if st.button('요약'):
            st.info('임의의 대화내역')
    with tab3:
        st.markdown("##### 현재 진행중인 사업")

        st.markdown("##### 사례관리 진행상황(개별 대시보드에 있는 활동그래프)")

        st.info('상담자의 요청사항')
        if st.button('보기'):
            st.info('상담자의 요청사항을 입력하시오')
    with tab4:
        #메모장 기능(특이사항 입력)
        st.markdown('##### 특이사항')
        memo = st.text_area('입력', height=200)
        save_button = st.button('저장')

        if save_button:
            with open('memo.txt', 'w', encoding='UTF-8') as file:
                file.write(memo)
                st.success('저장되었습니다')

        st.markdown("###### 저장된 메모")
        try:
            with open('memo.txt', 'r', encoding='UTF-8') as file:
                saved_memo = file.read()
                st.write(saved_memo)
        except FileNotFoundError:
            st.info('저장된 메모가 없습니다')


# page2 내용 구성하기
def page2():
    st.sidebar.header('통합 관리')
    st.sidebar.markdown('##### 참여 중인 청년들의 현황을 안내합니다.')
    
    # 제목 넣기
    st.markdown("## 통합 관리")
    
    # Include Bootstrap Icons CDN
    bootstrap_icons_cdn = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css"
    st.markdown(f'<link rel="stylesheet" href="{bootstrap_icons_cdn}">', unsafe_allow_html=True)    
    
    # 데이터프레임 불러오기
    df = pd.read_csv('original4.csv')

    # 중복된 행 제거, df2는 최신 회차만 남겨둔 데이터 프레임
    df2 = df.drop_duplicates(['이름'], keep='last')
    
    # 인덱스 초기화 
    df2.reset_index(drop=True, inplace=True)
    
    # 점수에 따라 위험도 분류
    def determine_risk_level(score):
        if score >= 85 and score <= 116:
            return '심각'
        elif score >= 65:
            return '경계'
        elif score >= 45:
            return '주의'
        else:  # 40 or less
            return '정상'
    
    df2['위험도'] = df2['Total(/116)'].apply(determine_risk_level)

    # Reorder columns to have 'Risk Level' at the beginning
    col_order = ['위험도'] + [col for col in df.columns if col != '위험도']
    df2 = df2[col_order]
    df3 = df2.drop(['위도', '경도', '회차', '날짜'], axis=1)
    
    # 위험도에 따라 색으로 표시하는 함수
    def color_isolation_score(val):
        color = '#f47560' if val == '심각' else '#e8a838' if val == '경계' else '#f1e15b' if val == '주의' else '#61cdbb'
        return f'background-color: {color}'
    
    # 오늘 상담 일정 안내(ㅇ)
    with st.container(border=True):
        # 오늘 날짜
        now_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
        formatted_date = now_date.strftime("%Y년 %m월 %d일")
        st.markdown(f"##### 오늘 상담 일정 <small><font color='#00498c'>{formatted_date}</font></small>", unsafe_allow_html=True)
        today_date = now_date.strftime("%Y-%m-%d")
        
        one_week_later = now_date + datetime.timedelta(days=7)
        one_week_later_date = one_week_later.strftime("%Y-%m-%d")
        # 상담일정을 최신 회차에서 일주일 후로 잡는걸로 가정할게용
        today_dispatch = df2[df2['날짜']==one_week_later_date]
        today_count = len(today_dispatch)
        if today_count > 0 :
            st.dataframe(today_dispatch)
        else:
            st.markdown("금일 상담 일정이 없습니다.")
    
    with st.container(border=True):
        ## 고립/은둔 청년 한눈에 보기
        cols = st.columns([0.15, 0.15, 0.15, 0.55])
        with cols[0]:
            st.markdown("##### 관리대상 정보")
        with cols[1]:
            on3 = st.toggle('생년월일')
        with cols[2]:
            on4 = st.toggle('주소')
        if not on3:
            df3 = df3.drop(columns='생년월일')
        if not on4:
            df3 = df3.drop(columns='주소')
            
            
        selected = pills("Label", ['전체', '정상', '주의', '경계', '심각'], ["🟡","😊", "😐", "😑", "😵"], label_visibility='collapsed')
        if selected == '전체':
            df3 = df3
        else:
            df3 = df3.loc[df3['위험도'] == selected]
        with st.expander('관리대상 차트(최근 점수 측정 기준)', expanded=True):
            # 위험도에 따른 색상 데이터 프레임에 입히기
            styled_df = df3.style.applymap(color_isolation_score, subset=['위험도'])
            st.dataframe(styled_df, hide_index=True)
        
        cols = st.columns(2)
        with cols[0]:
            with st.container(border=True):
                # 파이차트
                data_pie = [
                    { "id": "-", "label": "-", "value": 0, "color": "hsl(309, 70%, 50%)" }, # 얘는 지우면 안돼요! 색상 일부러 맞춰놓은거임. nivo색상 순서가 정해져있음음
                    { "id": "심각", "label": "심각", "value": df3.loc[df3['위험도'] == '심각'].shape[0], "color": "hsl(229, 70%, 50%)" },
                    { "id": "주의", "label": "주의", "value": df3.loc[df3['위험도'] == '주의'].shape[0], "color": "hsl(78, 70%, 50%)" },
                    { "id": "경계", "label": "경계", "value": df3.loc[df3['위험도'] == '경계'].shape[0], "color": "hsl(278, 70%, 50%)" },
                    { "id": "정상", "label": "정상", "value": df3.loc[df3['위험도'] == '정상'].shape[0], "color": "hsl(273, 70%, 50%)" }
                ]
                with elements("nivo_pie_chart"):
                    with mui.Box(sx={"height": 450}):
                        nivo.Pie(
                            data=data_pie,
                            margin={"top": 50, "right": 50, "bottom": 50, "left": 50},
                            innerRadius=0.5,
                            padAngle=0.7,
                            cornerRadius=3,
                            activeOuterRadiusOffset=8,
                            borderWidth=1,
                            borderColor={"from": "color", "modifiers": [["darker", 0.8]]},
                            arcLinkLabelsSkipAngle=10,
                            arcLinkLabelsTextColor="grey",
                            arcLinkLabelsThickness=2,
                            arcLinkLabelsColor={"from": "color"},
                            arcLabelsSkipAngle=10,
                            arcLabelsTextColor={"from": "color", "modifiers": [["darker", 4]]},
                        )
        # 최신 회차 찾아서 지난 회차와 factor별 해당 청년 변화 확인
        max_num = df['회차'].max()
        df3_1 = df.loc[df['회차'] == max_num - 1]
        df3_1.reset_index(drop=True, inplace=True)
        label_list = {'고립': 'Isolation', '정서적 지지 부족': 'Emotional Support', '사회성 결여': 'Socialization', '동기부여 부족': 'Motivation'}
        value=[]
        delta=[]
        for i, j in label_list.items():
            value.append(df3.loc[df3['고립/은둔 유형'] == j].shape[0])
            delta.append(df3.loc[df3['고립/은둔 유형'] == j].shape[0] - df3_1.loc[df3_1['고립/은둔 유형'] == j].shape[0])
        with cols[1]:
            with st.container(border=True):
                with elements("container"):
                    with mui.Box(sx={"height": 55}):
                        st.markdown('')
                        st.markdown('')
                        cols = st.columns(2)
                        with cols[0]:
                            st.markdown('###### 고립')
                            st.metric(label='',
                                      value=f'{value[0]}명',
                                      delta=f'{delta[0]}명'
                                     )

                            st.divider()

                            st.markdown('###### 정서적 지지 부족')
                            st.metric(label='',
                                      value=f'{value[1]}명',
                                      delta=f'{delta[1]}명'
                                     )
                        with cols[1]:
                            st.markdown('###### 사회성 결여')
                            st.metric(label='',
                                      value=f'{value[2]}명',
                                      delta=f'{delta[2]}명'
                                     )

                            st.divider()

                            st.markdown('###### 동기부여 부족')
                            st.metric(label='',
                                      value=f'{value[3]}명',
                                      delta=f'{delta[3]}명'
                                     )

    with st.container(border=True):
        ## 고립/은둔 청년 위치를 지도로 보기

        # 위도, 경도 정보가 담긴 csv파일 불러오기
        # df2 = pd.read_csv('original2.csv')
        # df3.dropna(axis=0, inplace=True)

        ## 고립/은둔 청년 지원 기관 csv파일 불러오기
        loc = pd.read_csv('고립은둔청년 지원기관.csv')

        # Initialize the map:   
        m = folium.Map(location=[37.496665, 127.062980], zoom_start=13) # 강남구 위도, 경도

        # Add points
        for idx, row in df2.iterrows():
            if row['위험도'] == '심각':
                folium.Marker(location=[row["위도"], row["경도"]], popup=folium.Popup(row['이름'], max_width=200), icon=folium.Icon(icon='user', color='red', prefix='fa')).add_to(m)
            elif row['위험도'] == '경계':
                folium.Marker(location=[row["위도"], row["경도"]], popup=folium.Popup(row['이름'], max_width=200), icon=folium.Icon(icon='user', color='orange', prefix='fa')).add_to(m)

        # 기관 표시
        for idx, row in loc.iterrows():
            folium.Marker(
                location=[row["위도"], row["경도"]],
                popup=folium.Popup(row['기관명'], max_width=500),
                icon=folium.Icon(icon='heart', color='green', prefix='fa')
            ).add_to(m)


        cols = st.columns(2)

        with cols[0]:
            # Display the map in Streamlit
            st.markdown("##### 주요 관리대상 위치")
            st_folium(m, width=725, height=500)

        with cols[1]:
            cols = st.columns(2)

            with cols[0]:
                st.markdown('###### 내 관리 대상')
                
                st.markdown('<i class="bi bi-people" style="font-size: 80px;"></i>', unsafe_allow_html=True)
                st.metric(label="", value=f"{df2.shape[0]}명", label_visibility='collapsed')
                
                st.markdown("""
            <style>
            .metric-spacing { margin-bottom: 20px; }
            </style>
            """, unsafe_allow_html=True)

                st.markdown("""
            <style>
            .metric-spacing { margin-bottom: 10px; }
            </style>
            """, unsafe_allow_html=True)

                st.markdown('###### 전체 관리 대상')

                st.markdown('<i class="bi bi-people-fill" style="font-size: 80px;"></i>', unsafe_allow_html=True)
                st.metric(label="", value="640명", label_visibility='collapsed')


            with cols[1]:
                st.markdown('###### 고립/은둔 점수 평균')
                average_score = df2['Total(/116)'].sum()/df2['Total(/116)'].count()
                previous_average = df3_1['Total(/116)'].sum()/df3_1['Total(/116)'].count()
                st.markdown('<i class="bi bi-emoji-smile" style="font-size: 80px;"></i>', unsafe_allow_html=True)
                st.metric(label="", value=average_score, delta=round(average_score - previous_average), delta_color="inverse", label_visibility='collapsed')

                st.markdown("""
            <style>
            .metric-spacing { margin-bottom: 10px; }
            </style>
            """, unsafe_allow_html=True)

                st.markdown('###### 전체 고립/은둔 점수 평균')
                st.markdown('<i class="bi bi-emoji-expressionless" style="font-size: 80px;"></i>', unsafe_allow_html=True)
                st.metric(label="", value='60.2', delta="-1", delta_color="inverse", label_visibility='collapsed')

## -------------------- ▼ 사이드 바를 구성해서 페이지 연결하기 ▼ --------------------

# 선택한 페이지 함수에 대한 딕셔너리 생성
page_functions = {'개별 관리': main_page, '통합 관리': page2}

# "어른이집" 페이지 선택
with st.sidebar:
    choose = option_menu("어른이집 관리🐣", ["개별 관리", "통합 관리"],
                         icons=['bi bi-person-fill-check', 'bi bi-clipboard-data'], # 아이콘 변경: https://icons.getbootstrap.com/
                         menu_icon="bi bi-emoji-smile", default_index=0,
                         styles={"container": {"padding": "5!important", "background-color": "#fafafa"},
                                 "icon": {"color": "#2a2415", "font-size": "25px"}, 
                                 "nav-link": {"color": "#2a2415", "font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                                 "nav-link-selected": {"background-color": "#ffd851"},
                                }
                        )

# 선택한 페이지 함수 실행
page_functions[choose]()

## -------------------------------------------------------------------------------------
