<?php

use App\Models\Subscription;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "web" middleware group. Make something great!
|
*/
use App\Notifications\WelcomeNotification;
use Illuminate\Support\Facades\Notification;


Route::get('/', function () {
    return redirect('admin');
});


Route::get('/welcome',function(){

$sub = Subscription::first();

Notification::route('mail',$sub->email)->notify(new WelcomeNotification());

});

use Illuminate\Support\Facades\Http;

route::get("/chat",function(){

    $bot_token="5993651211:AAHXZSE0eC-H1NsBFrqk4KZj7PibziqTj9I";
    $url = "https://api.telegram.org/bot".$bot_token."/getChat?chat_id=960719750";

    
    $response = Http::get($url);

    dump($response->status());
    dd($response->body());

});