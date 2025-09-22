#include<bits/stdc++.h>
using namespace std;

int main(){
    int t;
    cin>>t;
    while(t--){
        int n;
        cin>>n;
        vector<int> res(n);
        for(int i=0;i<n;i++)cin>>res[i];
        vector<int> ans(n);
        for(int i=0;i<n;i++)cin>>ans[i];
        if(res[n-1]!=ans[i-1]){
            cout<<"NO"<<endl;
            continue;
        }
        int i;
        for(i=n-1;i>=0;i--){
            if(res[i]!=ans[i]){
                res[i]^=res[i+1];
                if(res[i]!=ans[i]){
                cout<<"NO"<<endl;
                break;
                }
            }
        }
        if(i<0)cout<<"YES"<<endl;
    }
}