import string
import re
import logging
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from itertools import chain
import django.shortcuts
from django.apps import apps
from fuzzywuzzy import fuzz, process
from utils.views import write_output

Genus = apps.get_model('orchiddb', 'Genus')
GenusRelation = apps.get_model('orchiddb', 'GenusRelation')
Alliance = apps.get_model('orchiddb', 'Alliance')
Species = apps.get_model('orchiddb', 'Species')
Accepted = apps.get_model('orchiddb', 'Accepted')
Hybrid = apps.get_model('orchiddb', 'Hybrid')
Synonym = apps.get_model('orchiddb', 'Synonym')
epoch = 1740
alpha_list = string.ascii_uppercase
logger = logging.getLogger(__name__)


def search_match(request, partner=None):
    # from itertools import chain
    genus = ''
    tail = ''
    spcount = ''
    y = ''
    search_list = ()
    partial_spc = ()
    partial_hyb = ()
    result_list = []
    spc_list = []
    hyb_list = []
    if partner:
        partner = Partner.objects.get(pk=partner)
        author = Photographer.objects.get(pk=partner.author.author_id)
        spc_list = list(SpcImages.objects.filter(author=author).values_list('pid', flat=True).distinct())
        hyb_list = list(HybImages.objects.filter(author=author).values_list('pid', flat=True).distinct())

    role = 'pub'
    if 'role' in request.GET:
        role = request.GET['role']

    if 'search' in request.GET:
        search = request.GET['search'].strip()
    else:
        search = ''
    keyword = search
    if request.user.is_authenticated:
        write_output(request, keyword)
    if keyword:
        rest = keyword.split(' ', 1)
        if len(rest) > 1:
            tail = rest[1]
        keys = keyword.split()
        if len(keys[0]) < 3 or keys[0].endswith('.'):
            keys = keys[1:]
            x = keys
        else:
            keyword = ' '.join(keys)
            x = keys[0]            # This could be genus or species (or hybrid)

        if len(x) > 7:
            x = x[: -2]  # Allow for some ending variation
        elif len(x) > 5:
            x = x[: -1]

        if len(keys) > 1:
            y = keys[1]            # This could be genus or species (or hybrid)

        if len(y) > 7:
            y = y[: -2]  # Allow for some ending variation
        elif len(y) > 5:
            y = y[: -1]

        if keys:
            genus = Genus.objects.filter(genus__iexact=keys[0])
            if len(genus) == 0:
                genus = ''
        else:
            genus = ''
        if genus and len(genus) > 0:
            genus = genus[0].genus
        else:
            genus = ''

        temp_list = Species.objects.exclude(status__iexact='pending')
        if spc_list:
            temp_list = temp_list.filter(pid__in=spc_list)
        if hyb_list:
            temp_list = temp_list.filter(pid__in=hyb_list)

        if len(keys) == 1:
            search_list = temp_list.filter(species__icontains=keys[0]).order_by('status', 'genus', 'species')
            mylist = search_list.values('pid')
            partial_spc = temp_list.filter(species__icontains=x).exclude(pid__in=mylist).order_by(
                'status', 'genus', 'species')

        elif len(keys) == 2:
            search_list = temp_list.filter(species__iexact=keys[1]).order_by('status', 'genus', 'species')
            mylist = search_list.values('pid')
            partial_spc = temp_list.filter(Q(species__icontains=x) | Q(infraspe__icontains=y)
                                           | Q(species__icontains=y)).exclude(pid__in=mylist).order_by(
                'status', 'genus', 'species')

        elif len(keys) == 3:
            search_list = temp_list.filter((Q(species__iexact=keys[0]) & Q(infraspe__iexact=keys[2])) |
                                           (Q(genus__iexact=keys[0]) & Q(species__iexact=keys[1]) &
                                            Q(infraspe__iexact=keys[2]))).order_by('status', 'genus', 'species')
            mylist = search_list.values('pid')
            partial_spc = temp_list.filter(Q(species__icontains=x) | Q(species__icontains=keys[1])).exclude(
                pid__in=mylist).order_by('status', 'genus', 'species')

        elif len(keys) >= 4:
            search_list = temp_list.filter((Q(species__iexact=keys[0]) & Q(infraspe__iexact=keys[2]))
                                           | (Q(genus__iexact=keys[0]) & Q(species__iexact=keys[1])
                                              & Q(infraspe__iexact=keys[2]))).order_by('status', 'genus', 'species')
            mylist = search_list.values('pid')
            partial_spc = temp_list.filter(Q(species__icontains=keys[1]) | Q(infraspe__icontains=keys[3])).exclude(
                pid__in=mylist).order_by('status', 'genus', 'species')
        spcount = len(search_list)

        all_list = list(chain(search_list, partial_hyb, partial_spc))
        for x in all_list:
            short_grex = x.short_grex().lower()
            score = fuzz.ratio(short_grex, keyword)     # compare against entire keyword
            if score < 60:
                score = fuzz.ratio(short_grex, keys[0])  # match against the first term after genus

            # if score < 100:
            grex = x.grex()
            score1 = fuzz.ratio(grex.lower(), keyword.lower())
            if score1 == 100:
                score1 = 200
            if score1 > score:
                score = score1
            if score >= 60:
                result_list.append([x, score])

    result_list.sort(key=lambda k: (-k[1], k[0].name()))

    context = {'result_list': result_list, 'keyword': keyword,
               'tail': tail, 'genus': genus, 'spcount': spcount, 'search': search,
               'level': 'search', 'title': 'search_match', 'role': role, 'namespace': 'search', }
    return django.shortcuts.render(request, "search/search_match.html", context)


def search_fuzzy(request):
    min_score = 60
    search = ''
    search_list = []
    spc_list = []
    hyb_list = []

    role = 'pub'
    if 'role' in request.GET:
        role = request.GET['role']

    # if role='pub':
    #     partner = Partner.objects.get(pk=partner)
    #     author = Photographer.objects.get(pk=partner.author.author_id)
    #     spc_list = list(SpcImages.objects.filter(author=author).values_list('pid', flat=True).distinct())
    #     hyb_list = list(HybImages.objects.filter(author=author).values_list('pid', flat=True).distinct())

    if request.GET.get('search'):
        search = request.GET['search'].strip()
    send_url = '/search/search_match/?search=' + search + "&role=" + role
    keyword = search.lower()
    write_output(request, keyword)

    grexlist = Species.objects.exclude(status='pending')
    # Filter for partner specific list.
    if spc_list:
        grexlist = grexlist.filter(pid__in=spc_list)
    if hyb_list:
        grexlist = grexlist.filter(pid__in=hyb_list)

    perfect_list = grexlist
    rest = keyword.split(' ', 1)

    if len(rest) > 1:
        # First get genus by name (could be abbrev.)
        genus = rest[0]
        abrev = genus
        if not genus.endswith('.'):
            abrev = genus + '.'
        # Then find genus in Genus class, start with accepted if exists.
        matched_gen = Genus.objects.filter(Q(genus=rest[0]) | Q(abrev=abrev)).order_by('status')

        if not matched_gen:
            return HttpResponseRedirect(send_url)

        # Genus found, get genus object
        genus_obj = matched_gen[0]
        keyword = rest[1]
        # If genus is a synonym, get accepted name
        if genus_obj.status == 'synonym':
            matched_gen = Genus.objects.filter(Q(genus=genus_obj.gensyn.acc_id) | Q(abrev=genus_obj.gensyn.acc.abrev))
            if matched_gen:
                genus_obj = matched_gen[0]
            else:
                # For synonym genus, use conventional search
                return HttpResponseRedirect(send_url)

        # Get alliance associated to the genus_obj
        alliance_obj = Alliance.objects.filter(gen=genus_obj.pid)
        if alliance_obj:
            # Then create genus_list of all genus associated to the alliance.
            genus_list = list(Alliance.objects.filter(alid=alliance_obj[0].alid.pid).values_list('gen'))

            # Then create the search space of species/hybrids in all genera associated to each alliances.
            grexlist = grexlist.filter(gen__in=genus_list)
        else:
            # If alliance does not exist, just search on the genus alone
            grexlist = grexlist.filter(gen=genus_obj.pid)
    else:
        return HttpResponseRedirect(send_url)

    # Compute fuzzy score for all species in grexlist
    for x in grexlist:
        # If the first word is genus hint, compare species and the tail
        score = fuzz.ratio(x.short_grex().lower(), keyword)
        if score >= min_score:
            search_list.append([x, score])

    # Add the perfect match and set score 100%.
    # At this point, the first word is related to a genus
    perfect_list = perfect_list.filter(species__iexact=rest[1])
    perfect_pid = perfect_list.values_list('pid', flat=True)

    perfect_items = []
    for x in perfect_pid:
        s = Species.objects.get(pk=x)
        y = [s, 100]
        perfect_items.append(y)

    species_temp = []
    for x in search_list:
        if x[0].pid not in perfect_pid:
            species_temp.append(x)

    # search_list = [item for item in search_list if item[0] not in perfect_pid]
    search_list = species_temp + perfect_items

    for i in range(len(search_list)):
        if genus_obj != '':
            if search_list[i][0].gen.pid == genus_obj.pid:
                if search_list[i][1] == 100:
                    search_list[i][1] = 200

    search_list.sort(key=lambda k: (-k[1], k[0].name()))
    context = {'search_list': search_list, 'len': len(search_list), 'search':  search, 'genus': genus,
               'alliance_obj': alliance_obj, 'genus_obj': genus_obj,
               'min_score': min_score, 'keyword': keyword,
               'level': 'search', 'title': 'fuzzy', 'role': role, 'namespace': 'search',

               }
    return django.shortcuts.render(request, "search/search_fuzzy.html", context)
