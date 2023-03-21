<?php

namespace App\Jobs;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldBeUnique;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Spatie\WebhookClient\Models\WebhookCall;
use Log;
use App\Actions\StoreSubscriptionAction;
use Carbon\Carbon;
use App\Notifications\WelcomeNotification;
use Illuminate\Support\Facades\Notification;

class CheckoutSessionCompleted implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

  
    public $webhookCall;

    public function __construct(WebhookCall $webhookCall)
    {
        $this->webhookCall = $webhookCall;
    }

    public function handle(StoreSubscriptionAction $StoreSubscriptionAction): void
    {

        $payload = $this->webhookCall->payload;

        

        if($payload['data']['object']['payment_status'] == "paid"){

            $data = [
            
                'telegram_user_id' => $payload['data']['object']['custom_fields'][0]['text']['value'],
                'product_name' => $payload['data']['object']['metadata']['product'],
                'number_of_sessions' => $payload['data']['object']['metadata']['number_of_session'],
                'uptime' => 0,
                'welcome_message_sent' => false,
                'email' => $payload['data']['object']['customer_details']['email'],
                'updated_at' => Carbon::now(),
                'updated_at' => Carbon::now(),
            ];

            $subscription = $StoreSubscriptionAction->execute($data);

            Notification::route('mail',$subscription->email)->notify(new WelcomeNotification());

        }

        
        // Log::info($payload);
        // Log::info($payload['data']['object']['custom_fields'][0]['text']['value']);
        // Log::info($payload['data']['object']['metadata']['product']);
        // Log::info($payload['data']['object']['metadata']['number_session']);
        // Log::info($payload['data']['object']['payment_status']);

    }


}
