<?php

namespace App\Notifications;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Notifications\Notification;

class WelcomeNotification extends Notification
{
    use Queueable;

  
    public function __construct()
    {
        //
    }

    
    public function via(object $notifiable): array
    {
        return ['mail'];
    }

   
    public function toMail($email): MailMessage
    {
        return (new MailMessage)->markdown('mail.welcome',['url' => "t.me/astrology"]);
    }


    public function toArray(object $notifiable): array
    {
        return [
            //
        ];
    }
}
