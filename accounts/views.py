from connections import connector
import config
import generic
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

current_section = 'accounts'

def index(request):
    '''
    Handler for the accounts
    '''
    sections = generic.getSiteSections(current_section)
    
    accounts = generic.getAllAccounts(connector)
    transactions = generic.getTransactions(connector = connector, reverse_order = True)
    
    # find the first transaction for each account
    for account in accounts:
        for transaction in transactions:
            if account['name'] == transaction['account']:
                account['last_activity'] = generic.twitterizeDate(transaction['time'])
                break
        else:
            account['last_activity'] = "never"
    
    page_title = "Accounts"
    context = {'globals': config.MainConfig['globals'], 'breadcrumbs': generic.buildBreadcrumbs(current_section, 'all'), 'page_title': page_title, 'page_sections': sections, 'accounts': accounts}
    return render(request, 'accounts/index.html', context)

def add(request):
    '''
    Handler for the account create form
    '''
    context = getAddAccountFormContext()
    context['breadcrumbs'] = generic.buildBreadcrumbs(current_section, '', 'Create')
    return render(request, 'accounts/add.html', context)

def getAddAccountFormContext(account_name='', currency='btc', error=None):
    '''
    Provide a common context between the account view and create account view
    '''
    # get available currencies
    currencies_available = []
    currencies = connector.services.keys()
    for curr in currencies:
        currencies_available.append({'name': curr, 'title': connector.config[curr]['currency_name']})
        
    page_title = "Create account"
    sections = generic.getSiteSections(current_section)
    context = {'globals': config.MainConfig['globals'], 'page_sections': sections, 'page_title': page_title, 'currencies': currencies_available, 'account_name': account_name, 'currency': currency, 'selected_currency': currency, 'error_message': error}
    return context

def create(request):
    '''
    Handler for POST of create account form
    '''
    try:
        account_name = request.POST['account_name']
        currency = request.POST['currency']
        if not account_name:
            raise Exception('Account name not provided')
    except (Exception, KeyError) as e:
        context = getAddAccountFormContext(account_name=account_name, currency=currency, error=e)
        return render(request, 'accounts/add.html', context)
    else:
        # all ok, create account
        new_address = connector.getnewaddress(currency, account_name)
        return HttpResponseRedirect(reverse('accounts:index'))
        
def details(request, account_address="pipes"):
    '''
    Handler for the account details
    '''

    # add a list of pages in the view
    sections = generic.getSiteSections(current_section)
    
    # get account details
    account = connector.getaccountdetailsbyaddress(account_address)
        
    # get transaction details
    transactions = generic.getTransactionsByAccount(connector, account['name'], account['currency'], reverse_order=True)
    generic.prettyPrint(account)
    
    page_title = "Account details for %s" % (account['name'] or account['alternative_name'])
    context = {
               'globals': config.MainConfig['globals'], 
               'breadcrumbs': generic.buildBreadcrumbs(current_section, '', account['name'] or account['alternative_name']), 
               'page_title': page_title, 
               'page_sections': sections, 
               'account': account,
               'transactions': transactions,
               }
    return render(request, 'accounts/details.html', context)
    