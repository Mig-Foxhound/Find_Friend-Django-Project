from django.shortcuts import render, redirect
from django.db import connection
from .forms import ProfileForm, LocationForm, SearchLocationForm
import populartimes
import datetime
import math
from mycrawl import popCrawl


def index(request):

    # Render the HTML template index.html with the data in the context variable.
    return render(
        request,
        'index.html',
    )


def CreateUser(request):
    return render(request, 'catalog/user_info_create.html')

def str2list(in_str):
    return in_str.split(',')

def list2str(in_list):
    return ",".join(in_list)


def InsertUserForm(request):
    if request.method == "POST":
        prof = ProfileForm(request.POST)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Profile WHERE Profile.userid = %s", [str(request.user.id)])
            row = cursor.fetchall()
            # update Profile table
            if len(row) == 0:
                cursor.execute("INSERT INTO Profile(name, netid, phone, userid) VALUES(%s, %s, %s, %s)", [prof.data['name'], prof.data['netid'], prof.data['phone'], str(request.user.id)])
            else:
                return render(request, 'catalog/user_info_duplicate.html')


            # prof.data['course'] is a comma seperated string
            course_list = str2list(prof.data['course'])
            for c in course_list:
                cursor.execute("INSERT INTO Course(netid, course) VALUES(%s, %s)", [prof.data['netid'], c])

        return redirect('user-detail')

def UserUpdate(request):
    return render(request, 'catalog/user_info_update.html')

def UpdateUserForm(request):
    if request.method == "POST":
        prof = ProfileForm(request.POST)
        with connection.cursor() as cursor:
            cursor.execute("SELECT netid FROM Profile WHERE Profile.userid = %s", [str(request.user.id)])
            row = cursor.fetchall()
            if len(row) == 0:
                print("User does not exists in Profile, please insert user info before update!!!")
            else:
                if prof.data['name']:
                    cursor.execute("UPDATE Profile SET name=%s WHERE Profile.netid = %s", [prof.data['name'], row[0]])
                if prof.data['phone']:
                    cursor.execute("UPDATE Profile SET phone=%s WHERE Profile.netid = %s", [prof.data['phone'], row[0]])

                if prof.data['course']:
                    # delete all existing courses for this user
                    cursor.execute("DELETE FROM Course WHERE Course.netid = %s", [row[0]])
                    # then insert new courses one by one
                    course_list = str2list(prof.data['course'])
                    for c in course_list:
                        cursor.execute("INSERT INTO Course(netid, course) VALUES(%s, %s)",
                                       [row[0], c])
    # print('User Info Upated')
    return redirect('user-detail')


def UserDetail(request):
    if request.method == "GET":
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Profile WHERE Profile.userid = %s", [str(request.user.id)])
            row = cursor.fetchall()
            if len(row) == 0:
                print("User does not exists, please register first!!!")
                return render(request, 'catalog/user_info_not_found.html')
            else:
                cursor.execute("SELECT * FROM Course WHERE Course.netid = %s", [row[0][1]])
                row_course = cursor.fetchall()
                c_list = []
                for item in row_course:
                    c_list.append(item[1])
                c_str = list2str(c_list)

            # Render the HTML template index.html with the data in the context variable.
            return render(
                request,
                'catalog/user_info.html',
                context={'Name': row[0][0],
                         'netid': row[0][1],
                         'phone': row[0][2],
                         'course': c_str,
                         })

def UserDelete(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT netid FROM Profile WHERE Profile.userid = %s", [str(request.user.id)])
        row = cursor.fetchall()
        cursor.execute("DELETE FROM Profile WHERE Profile.netid = %s", [row[0]])
        cursor.execute("DELETE FROM Course WHERE Course.netid = %s", [row[0]])
    return render(request, 'catalog/user_info_deleted.html')

def getDist(lat1, lon1, lat2, lon2):

    lat1, lon1 = float(lat1), float(lon1)
    lat2, lon2 = float(lat2), float(lon2)
    R = 3961
    dlon = (lon2 - lon1) * math.pi /180
    dlat = (lat2 - lat1) * math.pi /180

    a = (math.sin(dlat/2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin(dlon/2))**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c

    return distance


def UserMatch(request):
    if request.method == "POST":
        place_name = SearchLocationForm(request.POST).data['name']
        print(str(place_name))
        distanceLimit = SearchLocationForm(request.POST).data['distanceLimit']
        with connection.cursor() as cursor:
            cursor.execute("SELECT Course.course FROM Course INNER JOIN Profile ON Course.netid = Profile.netid WHERE Profile.userid = %s", [str(request.user.id)])
            self_course = set(cursor.fetchall())

            cursor.execute("SELECT * FROM Place WHERE Place.name = %s", [place_name])
            location = cursor.fetchall()[0]

            name = location[0]
            longitude = location[1]
            latitude = location[2]
            crowdedness = location[3]
            type = location[4]

            candidates = []
            range = float(distanceLimit)
            cursor.execute("SELECT * FROM Location")
            user_location = cursor.fetchall()
            for item in user_location:
                distance = getDist(item[2], item[1], latitude, longitude)
                if distance < range:
                    candidates.append(item[0])

            final_list = []
            for student in candidates:
                cursor.execute("SELECT Course.course FROM Course WHERE Course.netid = %s", [student])
                row_course = set(cursor.fetchall())
                if self_course.intersection(row_course):
                    final_list.append(student)

    return render(request, 'catalog/user_match.html', context={'userList': final_list})

def UserDeleted(request):
    return redirect("logout")

def Search(request):
    return redirect('user-detail')
    
def CrawlMyPop(request):
    mycrawl = popCrawl()
    mycrawl.engine(request)
    return redirect('user-detail')

def CrawlPopularity(request):
    popdata_library = populartimes.get("AIzaSyB0RALv_IqPawmS5eeLWfJBVtcAE8vCW98", ["library"], (40.116193536286815, -88.2435300726317), (40.08857770924527, -88.2047958483285))
    popdata_cafe = populartimes.get("AIzaSyB0RALv_IqPawmS5eeLWfJBVtcAE8vCW98", ["cafe"], (40.116193536286815, -88.2435300726317), (40.08857770924527, -88.2047958483285))
    # for item1 in popdata_library:
    #     facility = populartimes.get_id("AIzaSyB0RALv_IqPawmS5eeLWfJBVtcAE8vCW98",item1['id'])
    #     if 'current_popularity' not in facility:
    #         facility['current_popularity'] = None

    #     print(item1['name'], item1['coordinates']['lng'], item1['coordinates']['lat'], facility['current_popularity'])
    to_weekday = {1:"Monday",2:"Tuesday",3:"Wednesday", 4:"Thursday", 5:"Friday",6:"Saturday",7:"Sunday"}
    today = to_weekday[datetime.datetime.today().weekday()]

    with connection.cursor() as cursor:
        for item1, item2 in zip(popdata_library, popdata_cafe):
            library = populartimes.get_id("AIzaSyB0RALv_IqPawmS5eeLWfJBVtcAE8vCW98",item1['id'])
            cafe = populartimes.get_id("AIzaSyB0RALv_IqPawmS5eeLWfJBVtcAE8vCW98",item2['id'])
            if 'current_popularity' not in library:
                library['current_popularity'] = 0

            if 'current_popularity' not in cafe:
                cafe['current_popularity'] = 0
            try:
                cursor.execute("INSERT INTO Place(name, longitude, latitude, crowdedness, type) VALUE (%s, %s, %s, %s, %s)",\
                    [str(item1['name']), \
                        str(item1['coordinates']['lng']), str(item1['coordinates']['lat']), \
                        str(library['current_popularity']),\
                            "Library"])
            except:
                pass
            try:
                cursor.execute("INSERT INTO Place(name, longitude, latitude, crowdedness, type) VALUE (%s, %s, %s, %s, %s)",\
                    [str(item2['name']), \
                        str(item2['coordinates']['lng']), str(item2['coordinates']['lat']), \
                        str(cafe['current_popularity']),
                        "Cafe"])
            except:
                pass

    return redirect("user-detail")

def UpdateLocation(request):
    if request.method == "POST":
        location = LocationForm(request.POST)
        print(location)
    return redirect('user-insert')

def SearchLocation(request):
    if request.method == "POST":
        curLongitude = LocationForm(request.POST).data['longitude']
        curLatitude = LocationForm(request.POST).data['latitude']
        locationType = SearchLocationForm(request.POST).data['locationType']
        print (locationType, curLongitude, curLatitude)
        distanceLimit = SearchLocationForm(request.POST).data['distanceLimit']
        print (distanceLimit)
        placeList = []
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Place WHERE Place.type = %s", [str(locationType)])
            row_location = cursor.fetchall()
            for location in row_location:
                print (location)
                name = location[0]
                longitude = location[1]
                latitude = location[2]
                crowdedness = location[3]
                type = location[4]

                lat1, lon1 = 40.113746, -88.221730
                lat2, lon2 = 40.091162, -88.239937
                if curLongitude and curLatitude:
                    lat1, lon1 = float(curLatitude), float(curLongitude)
                if (longitude) and (latitude):
                    lat2, lon2 = float(latitude), float(longitude)
                R = 3961
                dlon = (lon2 - lon1)* math.pi /180
                dlat = (lat2 - lat1)* math.pi /180

                a = (math.sin(dlat/2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin(dlon/2))**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a) )
                distance = R * c

                range = float(distanceLimit)
                if distance < range:
                    placeList.append((name, type, crowdedness, distance))

        sortedPlaceList = sorted(placeList, key = lambda x: x[3])
        return render(
            request,
            'catalog/match_location.html',
            context={'allPlaces' : sortedPlaceList}
        )

def MatchUser(request):
    return render(request, "catalog/match_user.html")

def MatchPlace(request):
    return render(request, "catalog/match_location.html")

# def PlaceDetail(request, placeId):
#     if request.method == "GET":
#         placeName = ""
#         if placeId == 1:
#             placeName = "Grainger Library"
#         elif placeId == 2:
#             placeName = "UGL"
#         elif placeId == 3:
#             placeName = "Main Library"
#         elif placeId == 4:
#             placeName = "ECEB"
#         elif placeId == 5:
#             placeName = "Siebel Center"
#
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT crowdness FROM catalog_place WHERE name = %s",[placeName])
#         crowdness = cursor.fetchone()
#         if crowdness:
#             crowdness = crowdness[0]
#         else:
#             crowdness = [0]
#         cursor.execute("SELECT COUNT(*) FROM catalog_location INNER JOIN catalog_place on catalog_location.placename = catalog_place.name WHERE catalog_place.name = %s GROUP BY(catalog_location.placename)",[placeName])
#         row = cursor.fetchone()
#         if row:
#             matched_user = row[0]
#         else:
#             matched_user = 0
#
#
#     return render(request, 'catalog/place.html', context={
#     'place_id':placeId,
#     'place_name':placeName,
#     'place_crowdedness': crowdness[0],
#     'matched_user_number': matched_user})
#
# def ReportCrowd(request, placeId):
#     if request.method == "POST":
#         place = PlaceForm(request.POST)
#         crowdness = place.data['crowdness']
#         crowdness = min(max(float(crowdness), 0.0), 1.0)
#
#         placeName = ""
#         if placeId == 1:
#             placeName = "Grainger Library"
#         elif placeId == 2:
#             placeName = "UGL"
#         elif placeId == 3:
#             placeName = "Main Library"
#         elif placeId == 4:
#             placeName = "ECEB"
#         elif placeId == 5:
#             placeName = "Siebel Center"
#         with connection.cursor() as cursor:
#             try:
#                 cursor.execute("INSERT INTO catalog_usercrowdness(user, place, crowdness) VALUE (%s, %s, %s)",[str(request.user.netid), placeName, crowdness])
#             except:
#                 cursor.execute("UPDATE catalog_usercrowdness SET user=%s, place=%s, crowdness=%s",[str(request.user.netid), placeName, crowdness])
#
#         return render(request, 'catalog/place.html', context={
#             'place_id':placeId,
#             'place_name':placeName,
#             # 'place_crowdedness':crowdness,
#             'place_distance':1.0})
