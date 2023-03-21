<?php

namespace Database\Seeders;

// use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        // \App\Models\User::factory(2)->create();

        // \App\Models\User::factory()->create([
        //     'name' => 'Test User',
        //     'email' => 'test@example.com',
        // ]);

        $plans = [
            [
                'name' => 'basic',
                'number_of_session' => 15,
                'price' => 9.9,
                'is_primary' => true,
                'description' => 'here description about the plan'
            ],
            [
                'name' => 'standard',
                'number_of_session' => 3,
                'price' => 3.9,
                'is_primary' => false,
                'description' => 'here description about the plan'
            ]
        ];


        DB::table('plans')->truncate();
        DB::table('plans')->insert($plans);

        
    }
}
